"""Bounded official HTML search. No PDF, external search engine or disk cache.

Source excerpts are not reviewed library texts. Heuristic redaction/risk flags
are not anonymisation or a legal basis for receipt of the original HTML.
"""
from contextlib import contextmanager
from datetime import date
import hashlib
import base64
import json
import os
import re
import threading
from pathlib import Path
from urllib.parse import urljoin, urlsplit, parse_qs
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from arn_client import ARNClient
from arn_library_client import SummaryLibraryClient, LibraryUnavailable, _json, valid_original_reference

DATABASE = 'https://adokweb.arn.se/referatwebb'
OVERVIEW = 'https://www.arn.se/om-arn/vagledande-beslut/'
COMMON = 'https://www.arn.se/vanligafall/'
COMMON_CATALOG_SHA256 = '536b426e6c407be1979011763140fe2d766f3bfbc61168b7dd932b305ff2eb2e'
CASE = re.compile(r'\b[0-9]{4}-[0-9]{5}\b')
NOTICE = ('Sökning i ARN:s offentliga HTML-sökgränssnitt och senaste beslutsöversikt, '
          'granskade källutdrag ur Vanliga fall samt godkända lokala referat. '
          'Vanliga fall är en separat pedagogisk källtyp. Inte alla ARN-ärenden. Källutdrag är inte '
          'lokalt godkänd lästext eller hela beslutet. Ingen PDF-hämtning.')
CATEGORY = {'boende': 'Bo', 'bostad': 'Bo', 'bo': 'Bo', 'allmänna': 'Allm',
            'allm': 'Allm', 'försäkring': 'Förs', 'förs': 'Förs', 'elektronik': 'El'}
HEALTH = re.compile(r'(?i)\b(sjuk\w*|demens\w*|psyk\w*|diagnos\w*|hälsa|hälso\w*|'
                    r'funktionsneds\w*|gravid\w*|läkemed\w*|medicin\w*|cancer\w*|'
                    r'sexuell\w*|religio\w*|etnisk\w*|fackfören\w*)\b')
CRIME = re.compile(r'(?i)\b(dömd\w*|misstänkt\w*|åtal\w*|brotts\w*|bedräg\w*|'
                   r'polisanm\w*|stöld\w*|stals|krimin\w*|penningtvätt\w*)\b')


class HTMLUnavailable(RuntimeError):
    pass


def case_control_id(case_number):
    """Opaque deterministic ID accepted by the existing revocation journal."""
    return 'BIB-WEB-' + hashlib.sha256(case_number.encode('ascii')).hexdigest()[:32].upper()


def safe_source(url):
    if type(url) is not str:
        return False
    p = urlsplit(url)
    return (p.scheme == 'https' and not p.username and not p.password and not p.port
            and not p.query and (url == DATABASE or
            p.netloc == 'www.arn.se' and
            (re.fullmatch(r'/om-arn/vagledande-beslut/(?:[a-z0-9-]+/)*', p.path) is not None
             or re.fullmatch(r'/vanligafall/[a-z0-9.-]+/', p.path) is not None))
            and (not p.fragment or re.fullmatch(r'[A-Za-z0-9_-]{1,120}', p.fragment)))


def valid_index_reference(value):
    """Existing references plus individually approved common-case HTML sources."""
    return valid_original_reference(value) or (
        type(value.get('original_case_number')) is str
        and CASE.fullmatch(value['original_case_number']) is not None
        and type(value.get('official_source_url')) is str
        and value['official_source_url'].startswith(COMMON)
        and safe_source(value['official_source_url']))


def _normal(text):
    return re.sub(r'\s+', ' ', text).strip()


def _tokens(text):
    return set(re.findall(r'[^\W_]+', text.casefold()))


def _minimized_excerpt(text):
    text = ARNClient.minimize_identifiers(_normal(text))
    # Public form snippets must not turn unlabelled contact data into output.
    text = re.sub(r'(?<!\d)(?:19|20)?\d{6}[-+]\d{4}(?!\d)', '[identifierare maskerad]', text)
    protected = {'ARN', 'EU', 'HD', 'HFD', 'NJA', 'SOU', 'RH', 'KO', 'AB'}
    def minimize_party(match):
        # A letter after an explicit company role is not a consumer initial.
        # Do not turn, for example, "Flygbolaget A har" into another party.
        company_role = re.search(r'\b(?:flygbolaget|företaget|banken|bolaget)\s+$',
                                 text[:match.start()], re.IGNORECASE)
        if match[1] in protected or company_role:
            return match.group()
        return 'konsumenten ' + match[2]
    text = re.sub(r'\b([A-ZÅÄÖ]{1,3})\s+(har|hade|begär|begärde|anser|ansåg|köpte|yrkade)\b',
                  minimize_party, text)
    # Conservative signals only: do not repeat potentially sensitive snippets.
    risk = 'potential_sensitive_context' if HEALTH.search(text) or CRIME.search(text) else 'none_detected_not_reviewed'
    if risk == 'potential_sensitive_context':
        return 'Källutdraget visas inte: potentiellt känsligt innehåll kräver separat granskning.', risk
    return text[:1600] + (' … [förkortat HTML-utdrag]' if len(text) > 1600 else ''), risk


def _row(case_number, text, category='', stamp='', source=DATABASE):
    excerpt, risk = _minimized_excerpt(text)
    return {'case_number': case_number, 'date': stamp or 'okänt', 'category': category or 'okänd',
            'summary': excerpt, 'source': source, 'source_link_kind': 'overview',
            'content_kind': 'official_html_excerpt', 'read_status': 'not_locally_approved',
            'source_kind': 'guiding_summary' if source == OVERVIEW else 'reference_database',
            'sensitive_context': risk, 'file_id': '', 'xsessiontag': ''}


class CommonCaseCatalog:
    """Pinned, locally reviewed source excerpts, NOT approved library texts.

    Reviewing source pages is a preparation step. This hash authenticates the
    snapshot; it does not grant a legal basis or public deployment approval.
    """
    def __init__(self, path=None, digest=None):
        self.path = Path(path) if path is not None else Path(__file__).with_name('common_case_catalog.json')
        self.digest = COMMON_CATALOG_SHA256 if digest is None else digest

    def search(self, query):
        if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_size > 1024 * 1024:
            raise LibraryUnavailable('Källkatalogen kunde inte verifieras.')
        raw, data = _json(self.path)
        if hashlib.sha256(raw).hexdigest() != self.digest:
            raise LibraryUnavailable('Källkatalogens innehållshash stämmer inte.')
        if (type(data) is not dict or set(data) != {'schema_version','source_kind','source_review','legal_status','source_checked_at','records'}
                or type(data['schema_version']) is not int or data['schema_version'] != 1 or data['source_kind'] != 'common_case_examples'
                or data['source_review'] != 'official_individual_html_verified'
                or data['legal_status'] != 'local_candidate_not_approved_for_public_deployment'
                or type(data['source_checked_at']) is not str
                or date.fromisoformat(data['source_checked_at']).isoformat() != data['source_checked_at']
                or type(data['records']) is not list or len(data['records']) > 1000):
            raise LibraryUnavailable('Källkatalogens struktur stämmer inte.')
        fields = {'case_number','date','category','title','summary','source','source_kind',
                  'source_link_kind','content_kind','read_status','sensitive_context'}
        seen, result = set(), []
        for row in data['records']:
            if (type(row) is not dict or set(row) != fields or any(type(v) is not str for v in row.values())
                    or not CASE.fullmatch(row['case_number']) or row['case_number'] in seen
                    or not safe_source(row['source']) or not row['source'].startswith(COMMON)
                    or row['source_kind'] != 'common_case_example' or row['source_link_kind'] != 'case_specific'
                    or row['content_kind'] != 'official_html_excerpt' or row['read_status'] != 'not_locally_approved'
                    or row['sensitive_context'] not in ('potential_sensitive_context','none_detected_not_reviewed')
                    or not row['title'].strip() or not row['summary'].strip()):
                raise LibraryUnavailable('Källkatalogens post kunde inte verifieras.')
            seen.add(row['case_number'])
            # Search only releasable fields, never withheld original context.
            hay = row['case_number'] + ' ' + row['title'] + ' ' + row['summary']
            if all(ARNClient._contains_term(hay, term) for term in _tokens(query)):
                result.append({**row, 'file_id':'', 'xsessiontag':'', 'source_checked_at':data['source_checked_at']})
        return result


class OfficialHTML:
    """Own session per search; forms, cookies and HTML live only for that call."""
    def __init__(self, session_factory=requests.Session, robots_check=None, common_catalog=None):
        self.session_factory = session_factory
        self.robots_check = robots_check or self._robots
        self.common_catalog = CommonCaseCatalog() if common_catalog is None else common_catalog

    @staticmethod
    def _robots(session, source_url):
        origin = 'https://' + urlsplit(source_url).netloc
        if origin not in ('https://adokweb.arn.se', 'https://www.arn.se'):
            return False
        with session.request('GET', origin + '/robots.txt', timeout=(5, 12),
                             stream=True, allow_redirects=False,
                             headers={'Accept': 'text/plain, */*'}) as response:
            if response.status_code == 404:
                return True
            response.raise_for_status()
            if response.status_code != 200 or 'text/plain' not in response.headers.get('Content-Type', '').lower():
                raise HTMLUnavailable('Källans robotsregler kunde inte verifieras.')
            body = bytearray()
            for chunk in response.iter_content(4096):
                body.extend(chunk)
                if len(body) > 65536:
                    raise HTMLUnavailable('Källans robotsregler överskred storleksgränsen.')
            policy = RobotFileParser()
            policy.parse(bytes(body).decode('utf-8', errors='replace').splitlines())
            return policy.can_fetch('Qysley-ARN-MCP', source_url)

    @staticmethod
    def _allowed(url):
        p = urlsplit(url)
        if p.scheme != 'https' or p.username or p.password or p.port:
            return False
        if p.netloc == 'www.arn.se':
            return p.path == '/om-arn/vagledande-beslut/' and not p.query
        if p.netloc != 'adokweb.arn.se':
            return False
        query = parse_qs(p.query, keep_blank_values=True)
        if p.path == '/referatwebb':
            return not p.query
        if p.path == '/digiforms/sessionInitializer' and query == {'processName': ['ARN_Referatwebb_process']}:
            return True
        # The site's ordinary HTML bootstrap uses this path too; never permit
        # fileId/pdf/session download parameters on it or on the viewer.
        return (p.path in ('/digiforms/sessionInitializer', '/digiforms/htmlViewer')
                and set(query) == {'xsessiontag'} and len(query['xsessiontag']) == 1
                and re.fullmatch(r'[A-Za-z0-9_-]{1,80}', query['xsessiontag'][0]) is not None)

    def _html(self, session, method, url, **kwargs):
        # Validate BEFORE every request/redirect, not after following an unsafe URL.
        for _ in range(5):
            if not self._allowed(url):
                raise HTMLUnavailable('Otillåten HTML-källväg.')
            with session.request(method, url, timeout=(5, 12), stream=True,
                                 allow_redirects=False, **kwargs) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    url = urljoin(url, response.headers.get('Location', ''))
                    if response.status_code in (301, 302, 303):
                        method, kwargs = 'GET', {}
                    continue
                response.raise_for_status()
                if 'text/html' not in response.headers.get('Content-Type', '').lower():
                    raise HTMLUnavailable('Källan levererade inte HTML.')
                body = bytearray()
                for chunk in response.iter_content(16384):
                    body.extend(chunk)
                    if len(body) > 2 * 1024 * 1024:
                        raise HTMLUnavailable('HTML-källan överskred storleksgränsen.')
                return BeautifulSoup(bytes(body).decode('utf-8', errors='replace'), 'html.parser'), url
        raise HTMLUnavailable('För många omdirigeringar från HTML-källan.')

    @staticmethod
    def _form_data(form):
        # Reuse the established public-form handling, never Legacy.get_decision.
        return ARNClient._extract_form_data(None, form)

    def database(self, session, query, category, outcome, first, last):
        soup, url = self._html(session, 'GET', DATABASE)
        form = soup.find('form')
        if form is None or not form.get('action'):
            raise HTMLUnavailable('ARN:s sökformulär saknas.')
        field, button = form.select_one('#input-search-referatwebb'), form.select_one('#btn-search')
        if field is None or not field.get('name') or button is None:
            raise HTMLUnavailable('ARN:s sökformulär har ändrats.')
        command = re.search(r"submitCmd\('([^']+)'\)", button.get('onclick', ''))
        if command is None:
            raise HTMLUnavailable('ARN:s sökkommando saknas.')
        data = self._form_data(form)
        data[field['name']] = query
        data[ARNClient.CATEGORY_FIELD] = CATEGORY.get(category.casefold(), category)
        data[ARNClient.OUTCOME_FIELD] = outcome
        if first:
            data[ARNClient.FROM_DATE_FIELD] = first + '-01-01'
        if last:
            data[ARNClient.TO_DATE_FIELD] = last + '-12-31'
        data[command.group(1)] = 'submit'
        soup, _ = self._html(session, 'POST', urljoin(url, form['action']), data=data)
        # An empty response must still be the expected HTML application, not a
        # 200 login/challenge/error page silently presented as zero matches.
        if soup.select_one('#input-search-referatwebb') is None:
            raise HTMLUnavailable('ARN:s HTML-svar kunde inte verifieras.')
        rows = []
        for container in soup.select('.case-container')[:100]:
            for element in container.select('script,style,button,input'):
                element.decompose()
            text = _normal(container.get_text(' ', strip=True))
            case = CASE.search(text)
            if case is None:
                continue
            stamp = re.search(r'\b\d{4}-\d{2}-\d{2}\b', text)
            cat = next((c for c in ARNClient.KNOWN_CATEGORIES if ARNClient._contains_term(text, c)), '')
            rows.append(_row(case.group(), text, cat, stamp.group() if stamp else ''))
        return rows

    def overview(self, session, query):
        soup, _ = self._html(session, 'GET', OVERVIEW)
        if not soup.find('h1') or 'vägledande' not in soup.find('h1').get_text().casefold():
            raise HTMLUnavailable('ARN:s beslutsöversikt kunde inte verifieras.')
        rows = []
        for heading in soup.find_all('h3'):
            blocks, links = [], []
            for sibling in heading.next_siblings:
                if getattr(sibling, 'name', None) in ('h2', 'h3', 'hr'):
                    break
                if getattr(sibling, 'name', None) in ('p', 'ul', 'ol', 'div'):
                    blocks.append(sibling.get_text(' ', strip=True))
                    links.extend(sibling.find_all('a'))
            text = _normal(' '.join(blocks))
            references = {CASE.search(a.get_text()).group() for a in links if CASE.search(a.get_text())}
            if len(references) != 1:
                continue  # no guessing a reference from an unrelated legal citation
            case = next(iter(references))
            title = heading.get_text(' ', strip=True)
            stamp = re.search(r'\b\d{4}-\d{2}-\d{2}\b', title)
            row = _row(case, text, title.split(',')[0].strip(), stamp.group() if stamp else '', OVERVIEW)
            if query and not all(ARNClient._contains_term(row['summary'] + ' ' + row['category'] + ' ' + case, term)
                                 for term in _tokens(query)):
                continue
            for a in links:
                candidate = urljoin(OVERVIEW, a.get('href', ''))
                if case in a.get_text() and candidate != OVERVIEW and safe_source(candidate):
                    row.update(source=candidate, source_link_kind='case_specific')
                    break
            rows.append(row)
        return rows

    def search(self, query, category='alla', outcome='obegransad', first='', last=''):
        rows, states = [], {}
        common = self.common_catalog.search(query) if self.common_catalog != () else []
        if CASE.fullmatch(query.strip()) and any(r['case_number'] == query.strip() for r in common):
            # An exact known reference needs no live whole-page processing.
            return common if outcome == 'obegransad' else [], {
                'database':'not_consulted', 'latest_overview':'not_consulted', 'common_case_examples':'ok'}
        with self.session_factory() as session:
            session.headers.update({'User-Agent': 'Qysley-ARN-MCP/1.0.5 (official HTML only)',
                                    'Accept': 'text/html', 'Cache-Control': 'no-store'})
            for name, operation in [('database', lambda: self.database(session, query, category, outcome, first, last)),
                                    ('latest_overview', lambda: self.overview(session, query))]:
                try:
                    source_url = DATABASE if name == 'database' else OVERVIEW
                    if self.robots_check(session, source_url) is not True:
                        states[name] = 'disallowed_by_robots'
                        continue
                    batch = operation()
                    # Overview has no verified structured outcome field.
                    if name == 'latest_overview' and outcome != 'obegransad':
                        batch = []
                    rows.extend(batch)
                    states[name] = 'ok'
                except (requests.RequestException, HTMLUnavailable, ValueError, KeyError, TypeError):
                    states[name] = 'unavailable'
            if self.common_catalog != ():
                # No live refetch of 52 source pages for every user question.
                # Integrity failures intentionally propagate and fail closed.
                if outcome == 'obegransad':
                    rows.extend(common)
                states['common_case_examples'] = 'ok'
        if not rows and all(v != 'ok' for v in states.values()):
            raise HTMLUnavailable('ARN:s HTML-källor är inte tillgängliga.')
        return rows, states


class LocalIndexSource:
    """No discovery or network fallback. Approved rows come from the base reader."""
    def search(self, *args):
        return [], {'reviewed_index': 'ok'}


class BroadHTMLClient(SummaryLibraryClient):
    """Existing reviewed reader plus distinct live source-excerpt search."""
    def __init__(self, *args, source=None, enabled=None, source_mode=None, **kwargs):
        self._html_state = threading.local()
        self.source_mode = source_mode or os.environ.get('ARN_BROAD_SOURCE_MODE', 'reviewed_index')
        if self.source_mode not in ('official_html', 'reviewed_index'):
            raise LibraryUnavailable('Ogiltigt källäge.')
        if self.source_mode == 'reviewed_index' and source is not None:
            raise LibraryUnavailable('Indexläget tillåter ingen extern källadapter.')
        self.html = (LocalIndexSource() if self.source_mode == 'reviewed_index'
                     else source if source is not None else OfficialHTML())
        self.enabled = os.environ.get('ARN_BROAD_HTML_ENABLED') == '1' if enabled is None else enabled
        super().__init__(*args, **kwargs)

    @staticmethod
    def _valid_record(row):
        if type(row) is not dict:
            return False
        # Reuse all existing summary-field, hash and approval checks. Only the
        # additional official HTML source family needs separate URL validation.
        source = row.get('official_source_url')
        if type(source) is str and source.startswith(COMMON):
            if not valid_index_reference(row):
                return False
            plain = {k:v for k,v in row.items() if k not in ('original_case_number','official_source_url')}
            return SummaryLibraryClient._valid_record(plain)
        return SummaryLibraryClient._valid_record(row)

    @staticmethod
    def _reviewed_metadata(row):
        source = row.get('official_source_url', '')
        common = type(source) is str and source.startswith(COMMON)
        row.update(content_kind='reviewed_html_summary', read_status='locally_approved',
                   source_link_kind='case_specific' if common or source and source != OVERVIEW else 'overview',
                   sensitive_context='individually_reviewed')
        if common:
            row['source_kind'] = 'common_case_example'
        return row

    @contextmanager
    def exposure_guard(self):
        with super().exposure_guard():
            outer = not getattr(self._html_state, 'depth', 0)
            self._html_state.depth = getattr(self._html_state, 'depth', 0) + 1
            if outer:
                self._html_state.rows = {}
                self._html_state.states = {}
                self._html_state.page = {}
            try:
                yield
            finally:
                self._html_state.depth -= 1
                if outer:
                    self._html_state.rows = {}
                    self._html_state.states = {}

    def coverage(self):
        index = self.source_mode == 'reviewed_index'
        return {'mode': 'reviewed_local_index' if index else 'official_html_and_reviewed_library',
                'notice': ('Endast individuellt godkända texter i det lokala indexet. '
                           'Vägledande referat och pedagogiska Vanliga fall märks separat. '
                           'Ingen livehämtning från ARN och ingen PDF-fallback.') if index else NOTICE,
                'broad_search_enabled': self.enabled,
                'sources': dict(getattr(self._html_state, 'states', {})),
                'database_result_limit': 100, 'whole_arn_database_claimed': False,
                'database_link': DATABASE, 'latest_overview_link': OVERVIEW,
                'common_case_source': COMMON,
                'unknown_dates_excluded_when_year_filter': True,
                'no_third_party_search_engine': True}

    def _exclusions(self, approved):
        _, revoked = self.revocations.read()
        _, raw = _json(self.library_path)
        rows = raw['records']
        known_ids = {r.get('library_id') for r in rows if type(r) is dict}
        # A missing old library tombstone cannot silently reappear via live search.
        if any(key not in known_ids and not key.startswith('BIB-WEB-') for key in revoked):
            raise LibraryUnavailable('Återkallade källreferenser måste stämmas av.')
        good = {r['library_id'] for r in approved}
        denied = {r.get('original_case_number') for r in rows if type(r) is dict and r.get('library_id') not in good}
        return denied, revoked

    @staticmethod
    def _query(query):
        if type(query) is not str or len(query) > 1000:
            raise ValueError('Använd en kort sakfråga utan personuppgifter.')
        if not query.strip():
            raise ValueError('Ange en sakfråga; tom sökning är inte tillåten.')
        clean = ARNClient.minimize_identifiers(query.strip())
        if clean != query.strip() or re.search(r'(?<!\d)(?:19|20)?\d{6}[-+]\d{4}(?!\d)', query):
            raise ValueError('Ange inte kontaktuppgifter eller personnummer i sökningen.')
        return clean

    @staticmethod
    def _search_request_hash(query, category, outcome, from_year, to_year):
        value = {'query': query, 'category': category, 'outcome': outcome,
                 'from_year': str(from_year or ''), 'to_year': str(to_year or '')}
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _cursor_encode(request_hash, snapshot_hash, offset):
        raw = json.dumps({'v': 1, 'q': request_hash, 's': snapshot_hash, 'o': offset},
                         sort_keys=True, separators=(',', ':')).encode('ascii')
        return base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii')

    @staticmethod
    def _cursor_decode(cursor, request_hash, snapshot_hash, length):
        if type(cursor) is not str or not 1 <= len(cursor) <= 512 or not re.fullmatch(r'[A-Za-z0-9_-]+', cursor):
            raise ValueError('Ogiltig fortsättningsmarkör; börja om sökningen.')
        try:
            raw = base64.urlsafe_b64decode(cursor + '=' * (-len(cursor) % 4))
            data = json.loads(raw.decode('ascii'))
        except (ValueError, UnicodeError, json.JSONDecodeError):
            raise ValueError('Ogiltig fortsättningsmarkör; börja om sökningen.') from None
        if (type(data) is not dict or set(data) != {'v', 'q', 's', 'o'} or data['v'] != 1
                or data['q'] != request_hash or data['s'] != snapshot_hash
                or type(data['o']) is not int or data['o'] <= 0 or data['o'] >= length):
            raise ValueError('Sökningen har ändrats eller markören är ogiltig; börja om sökningen.')
        return data['o']

    @staticmethod
    def _rank_key(row, query):
        tokens = _tokens(query)
        title = _tokens(str(row.get('title', '')))
        summary = _tokens(str(row.get('summary', '')))
        reasoning = _tokens(str(row.get('reasoning', '')))
        facts = _tokens(str(row.get('facts', '')))
        tags = _tokens(' '.join(str(x) for x in row.get('tags', []) if type(x) is str))
        score = (5 * len(tokens & title) + 3 * len(tokens & summary)
                 + 2 * len(tokens & reasoning) + len(tokens & facts)
                 + len(tokens & tags))
        phrase = ' '.join(query.casefold().split())
        if phrase and phrase in ' '.join(str(row.get('title', '')).casefold().split()):
            score += 4
        stable = row.get('library_id') or row.get('case_number') or row.get('original_case_number') or ''
        return (-score, str(stable))

    def search(self, query, category='alla', outcome='obegransad', from_year='', to_year='', cursor=None,
               page_size=20):
        with self.exposure_guard():
            query = self._query(query)
            if type(page_size) is not int or not 1 <= page_size <= 20:
                raise ValueError('Resultatgränsen måste vara mellan 1 och 20.')
            # Reuse existing input validation, filtering and fail-closed controls.
            local = super().search(query, category, outcome, from_year, to_year)
            approved = self._records()
            denied, revoked = self._exclusions(approved)
            if not self.enabled:
                raise HTMLUnavailable('Bred HTML-sökning är inte aktiverad för denna kandidat.')
            if self.source_mode == 'reviewed_index':
                # This branch is deliberately independent of self.html. Only the
                # base library reader can supply rows here; it verifies the exact
                # approval pin, record hash, status, revocation state and schema.
                # An injected/replaced source adapter can never become a fallback.
                self._html_state.states['reviewed_index'] = 'ok'
                result = {row['case_number']: row for row in local}
                for case in list(result):
                    if case in denied or CASE.fullmatch(case) and case_control_id(case) in revoked:
                        del result[case]
                rows = list(result.values())
                rows.sort(key=lambda r: self._rank_key(r, query))
                snapshot_hash = hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True,
                                                         separators=(',', ':')).encode('utf-8')).hexdigest()
                request_hash = self._search_request_hash(query, category, outcome, from_year, to_year)
                offset = self._cursor_decode(cursor, request_hash, snapshot_hash, len(rows)) if cursor is not None else 0
                page = rows[offset:offset + page_size]
                next_offset = offset + len(page)
                next_cursor = (self._cursor_encode(request_hash, snapshot_hash, next_offset)
                               if next_offset < len(rows) else None)
                for row in page:
                    self._reviewed_metadata(row)
                    self._html_state.rows[row['case_number']] = dict(row)
                self._html_state.page = {'total_matches': len(rows), 'result_limit': page_size,
                                         'next_cursor': next_cursor, 'has_more': next_cursor is not None}
                return page
            candidates, states = self.html.search(query, category, outcome, str(from_year or ''), str(to_year or ''))
            for name, state in states.items():
                # A later concept query must not hide an earlier partial error.
                if self._html_state.states.get(name) != 'unavailable':
                    self._html_state.states[name] = state
            by_ref = {r.get('original_case_number', r['library_id']): self._result(r) for r in approved}
            result = {r['case_number']: r for r in local}
            actual_cat = CATEGORY.get(category.casefold(), category).casefold()
            for row in candidates:
                case = row['case_number']
                if not CASE.fullmatch(case) or case in denied or case_control_id(case) in revoked:
                    continue
                if category != 'alla' and CATEGORY.get(row['category'].casefold(), row['category']).casefold() != actual_cat:
                    continue
                stamp = row['date']
                if from_year or to_year:
                    try:
                        year = date.fromisoformat(stamp).year
                    except ValueError:
                        continue
                    if from_year and year < int(from_year) or to_year and year > int(to_year):
                        continue
                value = by_ref.get(case, row)
                if (case in result and case not in by_ref
                        and result[case].get('source_kind') != 'common_case_example'
                        and value.get('source_kind') == 'common_case_example'):
                    continue
                result[case] = value
            for case in list(result):
                if CASE.fullmatch(case) and case_control_id(case) in revoked:
                    del result[case]
            rows = list(result.values())
            rows.sort(key=lambda r: self._rank_key(r, query))
            snapshot_hash = hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True,
                                                     separators=(',', ':')).encode('utf-8')).hexdigest()
            request_hash = self._search_request_hash(query, category, outcome, from_year, to_year)
            offset = self._cursor_decode(cursor, request_hash, snapshot_hash, len(rows)) if cursor is not None else 0
            page = rows[offset:offset + page_size]
            next_offset = offset + len(page)
            next_cursor = (self._cursor_encode(request_hash, snapshot_hash, next_offset)
                           if next_offset < len(rows) else None)
            for row in page:
                if row.get('content_kind') != 'official_html_excerpt':
                    self._reviewed_metadata(row)
                self._html_state.rows[row['case_number']] = dict(row)
            self._html_state.page = {'total_matches': len(rows), 'result_limit': page_size,
                                     'next_cursor': next_cursor, 'has_more': next_cursor is not None}
            return page

    def get_decision(self, case_number, file_id=None, xsessiontag=None):
        with self.exposure_guard():
            case = case_number.strip() if type(case_number) is str else ''
            approved = self._records()
            denied, revoked = self._exclusions(approved)
            if case in denied or CASE.fullmatch(case) and case_control_id(case) in revoked:
                raise LibraryUnavailable('Referatet är inte tillgängligt.')
            if any(case in (r['library_id'], r.get('original_case_number')) for r in approved):
                row = super().get_decision(case)
                return self._reviewed_metadata(row)
            if self.source_mode == 'reviewed_index':
                raise LibraryUnavailable('Beslutet finns inte i det godkända biblioteket.')
            if not CASE.fullmatch(case):
                raise LibraryUnavailable('Ogiltig ärendereferens.')
            row = getattr(self._html_state, 'rows', {}).get(case)
            if row is None:
                row = next((r for r in self.search(case) if r['case_number'] == case), None)
            if row is None:
                raise LibraryUnavailable('Ingen verifierad HTML-träff för referensen.')
            return {**row, 'text': 'Ingen lokalt godkänd lästext finns för detta ärende. '
                    'Tillgängligt HTML-sökutdrag och officiell källa visas ovan. '
                    'Ingen PDF eller ogranskad beslutstext har hämtats.'}

    def similar_cases(self, problem, category='alla', outcome='obegransad', from_year='', to_year='', max_results=10):
        with self.exposure_guard():
            query = self._query(problem)
            concepts = ARNClient._extract_concepts(self, query)
            queries = list(dict.fromkeys([query, *concepts[:2]]))
            rows = {}
            terms = _tokens(query)
            for term in queries:
                if term:
                    for row in self.search(term, category, outcome, from_year, to_year):
                        rows[row['case_number']] = row
            for row in rows.values():
                row['score'] = sum(ARNClient._contains_term(row['summary'], term) for term in terms)
            ranked = sorted(rows.values(), key=lambda r: (-r['score'], r['case_number']))
            ranked = [r for r in ranked if r['score'] > 0][:max(1, min(int(max_results), 20))]
            return {'concepts': [], 'results': ranked, 'common_cases': [], 'count': len(ranked)}

    _contains_term = staticmethod(ARNClient._contains_term)
