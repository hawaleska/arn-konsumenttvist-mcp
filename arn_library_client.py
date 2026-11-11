"""Local reviewed-text adapter. No network, PDF parsing or inherited live methods.

An approval is an operator decision bound to exact content, not proof of anonymity.
The approval-file digest must come from trusted configuration, not from that file.
"""
import hashlib
import hmac
import json
import os
import re
import threading
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

from arn_client import ARNClient as LegacyHelpers
from library_lifecycle import Revocations, ControlUnavailable, control_lock

SOURCE = 'urn:qysley:arn-library'
NOTICE = ('Endast godkända texter i det lokala beslutsbiblioteket. '
          'Begränsad täckning; bearbetade referat, inte ARN:s originalakt. '
          'Ingen automatisk hämtning från ARN.')
FIELDS = frozenset(('library_id', 'version', 'date', 'category', 'outcome',
                    'summary', 'facts', 'reasoning', 'disposition', 'companies', 'tags', 'synthetic'))
ID = re.compile(r'BIB-[A-Z0-9-]{1,64}\Z')
ORIGINAL_FIELDS = frozenset(('original_case_number', 'official_source_url'))
CASE_NUMBER = re.compile(r'[0-9]{4}-[0-9]{1,8}\Z')
OFFICIAL_SOURCE = re.compile(r'https://(?:www\.)?arn\.se/om-arn/vagledande-beslut/(?:[a-z0-9-]+/)*(?:#[A-Za-z0-9_-]{1,120})?\Z')
SHA = re.compile(r'[a-f0-9]{64}\Z')


def valid_original_reference(value):
    return (type(value.get('original_case_number')) is str
            and CASE_NUMBER.fullmatch(value['original_case_number']) is not None
            and type(value.get('official_source_url')) is str
            and OFFICIAL_SOURCE.fullmatch(value['official_source_url']) is not None)


class LibraryUnavailable(RuntimeError):
    pass


def content_sha256(record):
    return hashlib.sha256(json.dumps(record, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _json(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 32 * 1024 * 1024:
        raise LibraryUnavailable('Beslutsbiblioteket är inte tillgängligt.')
    data = path.read_bytes()
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate key')
            result[key] = value
        return result
    return data, json.loads(data, object_pairs_hook=unique)


class LibraryClient:
    minimize_identifiers = staticmethod(LegacyHelpers.minimize_identifiers)

    def __init__(self, library_path, approvals_path, approvals_sha256, *, allow_synthetic=False,
                 revocations_path=None, revocation_anchor_path=None, revocation_lock_path=None):
        self.library_path = Path(library_path)
        self.approvals_path = Path(approvals_path)
        self.approvals_sha256 = approvals_sha256
        self.allow_synthetic = allow_synthetic
        if not all((revocations_path, revocation_anchor_path, revocation_lock_path)):
            raise LibraryUnavailable('Bibliotekets kontrollstatus är inte tillgänglig.')
        self.revocations = Revocations(revocations_path, revocation_anchor_path, revocation_lock_path)
        content_roots = {self.library_path.resolve().parent, self.approvals_path.resolve().parent}
        if any(path.resolve().is_relative_to(root)
               for path in (self.revocations.journal, self.revocations.anchor, self.revocations.lock)
               for root in content_roots):
            raise LibraryUnavailable('Kontrollstatus får inte ingå i innehållsbackupen.')
        self._exposure = threading.local()
        # Startup must fail closed; later reads revalidate approval and content too.
        self._records()

    @classmethod
    def from_environment(cls):
        folder = Path(__file__).resolve().parent / 'library'
        return cls(os.environ.get('ARN_LIBRARY_PATH', folder / 'approved.json'),
                   os.environ.get('ARN_LIBRARY_APPROVALS', folder / 'approvals.json'),
                   os.environ.get('ARN_LIBRARY_APPROVALS_SHA256', ''),
                   allow_synthetic=os.environ.get('ARN_LIBRARY_ALLOW_SYNTHETIC') == '1',
                   revocations_path=os.environ.get('ARN_LIBRARY_REVOCATIONS'),
                   revocation_anchor_path=os.environ.get('ARN_LIBRARY_REVOCATION_ANCHOR'),
                   revocation_lock_path=os.environ.get('ARN_LIBRARY_REVOCATION_LOCK'))

    @contextmanager
    def exposure_guard(self):
        # Reentrant per thread: combined tools and serialization share one reader
        # lock. Operator commit cannot race response construction in another process.
        if getattr(self._exposure, 'depth', 0):
            yield
            return
        try:
            with control_lock(self.revocations.lock):
                self._exposure.depth = 1
                try:
                    yield
                finally:
                    self._exposure.depth = 0
        except ControlUnavailable:
            raise LibraryUnavailable('Bibliotekets kontrollstatus är inte tillgänglig.') from None

    @staticmethod
    def _valid_record(row):
        if type(row) is not dict or set(row) not in (FIELDS, FIELDS | ORIGINAL_FIELDS):
            return False
        if ORIGINAL_FIELDS & set(row) and not valid_original_reference(row):
            return False
        if type(row['library_id']) is not str or not ID.fullmatch(row['library_id']):
            return False
        if type(row['version']) is not int or row['version'] < 1 or type(row['synthetic']) is not bool:
            return False
        for key in ('category', 'summary', 'facts', 'reasoning', 'disposition'):
            if type(row[key]) is not str or not row[key].strip():
                return False
        if type(row['date']) is not str:
            return False
        if row['date']:
            try:
                if date.fromisoformat(row['date']).isoformat() != row['date']:
                    return False
            except ValueError:
                return False
        if row['outcome'] not in ('bifall', 'delvis bifall', 'avslag', 'annat'):
            return False
        return all(type(row[key]) is list and all(type(s) is str and s.strip() for s in row[key])
                   for key in ('companies', 'tags'))

    @staticmethod
    def _approved(approval, row):
        required = {'library_id', 'content_sha256', 'status', 'reviewer', 'reviewed_at',
                    'legal_review', 'identifiability_review', 'legal_fidelity_review'}
        if type(approval) is not dict or set(approval) != required:
            return False
        if approval['library_id'] != row['library_id'] or approval['status'] != 'approved':
            return False
        if any(approval[k] != 'approved' for k in
               ('legal_review', 'identifiability_review', 'legal_fidelity_review')):
            return False
        if type(approval['reviewer']) is not str or not approval['reviewer'].strip():
            return False
        try:
            stamp = datetime.fromisoformat(approval['reviewed_at'].replace('Z', '+00:00'))
            if stamp.tzinfo is None:
                return False
        except (ValueError, TypeError, AttributeError):
            return False
        digest = approval['content_sha256']
        return type(digest) is str and SHA.fullmatch(digest) and hmac.compare_digest(digest, content_sha256(row))

    def _records(self):
        with self.exposure_guard():
            return self._records_locked()

    def _records_locked(self):
        try:
            _, revoked = self.revocations.read()
            if type(self.approvals_sha256) is not str or not SHA.fullmatch(self.approvals_sha256):
                raise ValueError('missing trusted approval pin')
            raw, approvals = _json(self.approvals_path)
            if not hmac.compare_digest(hashlib.sha256(raw).hexdigest(), self.approvals_sha256):
                raise ValueError('approval digest')
            _, library = _json(self.library_path)
            if (type(library) is not dict or set(library) != {'schema_version', 'records'}
                    or type(library['schema_version']) is not int or library['schema_version'] != 1
                    or type(library['records']) is not list or type(approvals) is not dict
                    or set(approvals) != {'schema_version', 'approvals'}
                    or type(approvals['schema_version']) is not int or approvals['schema_version'] != 1
                    or type(approvals['approvals']) is not list):
                raise ValueError('schema')
            # Ambiguous duplicate IDs cannot inherit another row's approval.
            ids = [r.get('library_id') for r in library['records'] if type(r) is dict]
            aids = [a.get('library_id') for a in approvals['approvals'] if type(a) is dict]
            originals = [r.get('original_case_number') for r in library['records'] if type(r) is dict]
            rows = []
            for row in library['records']:
                if not self._valid_record(row):
                    continue
                key = row['library_id']
                if key in revoked:
                    continue
                if ids.count(key) != 1 or aids.count(key) != 1:
                    continue
                if 'original_case_number' in row and originals.count(row['original_case_number']) != 1:
                    continue
                if row['synthetic'] and not self.allow_synthetic:
                    continue
                approval = next(a for a in approvals['approvals'] if type(a) is dict and a.get('library_id') == key)
                if self._approved(approval, row):
                    rows.append(row)
            return rows
        except Exception:
            raise LibraryUnavailable('Beslutsbiblioteket är inte tillgängligt.') from None

    @staticmethod
    def _text(row):
        return '\n\n'.join(('Sakförhållanden\n' + row['facts'],
                             'Rättsliga skäl\n' + row['reasoning'],
                             'Utgång\n' + row['disposition']))

    @classmethod
    def _result(cls, row):
        result = {'case_number': row.get('original_case_number', row['library_id']), 'date': row['date'], 'category': row['category'],
                'summary': row['summary'], 'text': cls._text(row),
                'source': f"{SOURCE}:{row['library_id']}:v{row['version']}",
                # Existing combined-tool internal plumbing; never remote document handles.
                'file_id': row['library_id'], 'xsessiontag': ''}
        if 'original_case_number' in row:
            result.update(original_case_number=row['original_case_number'],
                          official_source_url=row['official_source_url'])
        return result

    @staticmethod
    def _tokens(text):
        return set(re.findall(r'[^\W_]+', text.casefold(), flags=re.UNICODE))

    def search(self, query, category='alla', outcome='obegransad', from_year='', to_year=''):
        query = self.minimize_identifiers((query or '').strip())
        category = (category or 'alla').strip().casefold()
        aliases = {'boende': 'bo', 'bostad': 'bo', 'elektronik': 'el', 'allmänna': 'allm',
                   'försäkring': 'förs'}
        category = aliases.get(category, category)
        def year(value):
            if value in ('', None):
                return None
            if not re.fullmatch(r'[0-9]{4}', str(value)):
                raise ValueError('Ogiltigt årfilter.')
            return int(value)
        first, last = year(from_year), year(to_year)
        if first is not None and last is not None and first > last:
            raise ValueError('Ogiltigt årfilter.')
        outcome = (outcome or 'obegransad').casefold()
        if outcome not in ('obegransad', 'bifall', 'delvis bifall', 'avslag', 'annat'):
            raise ValueError('Ogiltigt utfallsfilter.')
        wanted = self._tokens(query)
        results = []
        for row in self._records():
            actual = aliases.get(row['category'].casefold(), row['category'].casefold())
            if category != 'alla' and actual != category:
                continue
            if outcome != 'obegransad' and row['outcome'] != outcome:
                continue
            if first is not None or last is not None:
                if not row['date']:
                    continue
                y = int(row['date'][:4])
                if first is not None and y < first or last is not None and y > last:
                    continue
            hay = ' '.join([row['library_id'], row.get('original_case_number', ''), row['summary'], self._text(row),
                            *row['companies'], *row['tags']])
            overlap = wanted & self._tokens(hay)
            if wanted and not wanted.issubset(self._tokens(hay)):
                continue
            results.append((len(overlap), row))
        results.sort(key=lambda pair: (-pair[0], pair[1]['library_id']))
        return [self._result(row) for _, row in results]

    def get_decision(self, case_number, file_id=None, xsessiontag=None):
        # Ignore caller-provided document/session handles. Only the approved ID is used.
        matches = [row for row in self._records()
                   if case_number in (row['library_id'], row.get('original_case_number'))]
        if len(matches) == 1:
            return self._result(matches[0])
        raise LibraryUnavailable('Beslutet finns inte i det godkända biblioteket.')

    def similar_cases(self, problem, category='alla', outcome='obegransad', from_year='',
                      to_year='', max_results=10):
        query = self.minimize_identifiers((problem or '').strip())
        rows = self.search('', category, outcome, from_year, to_year) if query else []
        limit = max(1, min(int(max_results), 20))
        terms = self._tokens(query)
        for row in rows:
            row['score'] = len(terms & self._tokens(row['summary'] + ' ' + row['text']))
        rows = [row for row in rows if row['score'] > 0]
        rows.sort(key=lambda r: (-r['score'], r['case_number']))
        return {'concepts': [], 'results': rows[:limit], 'common_cases': [], 'count': len(rows[:limit])}
