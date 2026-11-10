"""Operator-only revocation metadata; no deletions, expiry, network or raw content.

The independently protected anchor is deliberately NOT part of content rollback.
Restoring that trust boundary too requires external latest-state reconciliation.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import time

ID = re.compile(r'BIB-[A-Z0-9-]{1,64}\Z')
CASE = re.compile(r'CASE-[A-F0-9]{24}\Z')


class ControlUnavailable(RuntimeError):
    def __init__(self):
        super().__init__('Bibliotekets kontrollstatus är inte tillgänglig.')


def _bytes(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')) + '\n').encode()


def _read(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 32 * 1024 * 1024:
        raise ControlUnavailable()
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ControlUnavailable()
            result[k] = v
        return result
    raw = path.read_bytes()
    return raw, json.loads(raw, object_pairs_hook=unique)


def _atomic_write(path, raw):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ControlUnavailable()
    previous = path.stat()
    fd, name = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            if os.name != 'nt':
                os.fchown(stream.fileno(), previous.st_uid, previous.st_gid)
                os.fchmod(stream.fileno(), stat.S_IMODE(previous.st_mode))
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        if os.name != 'nt':
            fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    finally:
        if os.path.exists(name):
            os.unlink(name)  # Only own incomplete temporary file; never journal data.


@contextmanager
def control_lock(path, *, writer=False, timeout=5):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ControlUnavailable()
    stream = path.open('r+b' if writer else 'rb')
    acquired = False
    try:
        deadline = time.monotonic() + timeout
        while True:
            try:
                if os.name == 'nt':
                    import msvcrt
                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK if writer else msvcrt.LK_NBRLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), (fcntl.LOCK_EX if writer else fcntl.LOCK_SH) | fcntl.LOCK_NB)
                acquired = True
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise ControlUnavailable() from None
                time.sleep(0.01)
        yield
    finally:
        if acquired:
            if os.name == 'nt':
                import msvcrt
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()


class Revocations:
    def __init__(self, journal, anchor, lock):
        self.journal, self.anchor, self.lock = map(Path, (journal, anchor, lock))
        resolved = [p.resolve() for p in (self.journal, self.anchor, self.lock)]
        if len(set(resolved)) != 3 or resolved[0].parent == resolved[1].parent:
            raise ControlUnavailable()

    def read(self):
        try:
            raw, journal = _read(self.journal)
            _, anchor = _read(self.anchor)
            if (type(journal) is not dict or set(journal) != {'schema_version', 'events'}
                    or type(journal['schema_version']) is not int or journal['schema_version'] != 1
                    or type(journal['events']) is not list
                    or type(anchor) is not dict or set(anchor) != {'schema_version', 'sequence', 'journal_sha256'}
                    or type(anchor['schema_version']) is not int or anchor['schema_version'] != 1
                    or type(anchor['sequence']) is not int or anchor['sequence'] != len(journal['events'])
                    or anchor['journal_sha256'] != hashlib.sha256(raw).hexdigest()):
                raise ControlUnavailable()
            seen = set()
            for i, event in enumerate(journal['events'], 1):
                if (type(event) is not dict or set(event) != {'sequence', 'library_id', 'request_ref', 'revoked_at'}
                        or type(event['sequence']) is not int or event['sequence'] != i
                        or type(event['library_id']) is not str or not ID.fullmatch(event['library_id'])
                        or type(event['request_ref']) is not str or not CASE.fullmatch(event['request_ref'])
                        or event['library_id'] in seen):
                    raise ControlUnavailable()
                if datetime.fromisoformat(event['revoked_at'].replace('Z', '+00:00')).tzinfo is None:
                    raise ControlUnavailable()
                seen.add(event['library_id'])
            return journal, seen
        except Exception:
            raise ControlUnavailable() from None


def initialize(journal, anchor, lock):
    """Explicit first initialization only, never automatic recovery on startup."""
    control = Revocations(journal, anchor, lock)
    paths = (control.journal, control.anchor, control.lock)
    if any(p.exists() or p.is_symlink() for p in paths):
        raise ControlUnavailable()
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    raw = _bytes({'schema_version': 1, 'events': []})
    # Exclusive creation prevents accidentally resetting an existing trust history.
    for path, data in [(control.lock, b'0'), (control.journal, raw),
                       (control.anchor, _bytes({'schema_version': 1, 'sequence': 0,
                                               'journal_sha256': hashlib.sha256(raw).hexdigest()}))]:
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    return control


def revoke(control, library_id, request_ref):
    """Permanent ID tombstone. A future approval/version cannot lift it.

    Same ID is idempotent. Record only an opaque rights-case reference, no name,
    email, original case number, reason or request text. Operator mandate needed.
    """
    if not ID.fullmatch(library_id) or not CASE.fullmatch(request_ref):
        raise ControlUnavailable()
    with control_lock(control.lock, writer=True):
        journal, seen = control.read()
        if library_id in seen:
            return {'revoked': True, 'already_revoked': True, 'sequence': len(journal['events'])}
        sequence = len(journal['events']) + 1
        journal['events'].append({'sequence': sequence, 'library_id': library_id,
                                  'request_ref': request_ref,
                                  'revoked_at': datetime.now(timezone.utc).isoformat()})
        raw = _bytes(journal)
        # If interrupted between files, readers see mismatch and fail closed.
        _atomic_write(control.journal, raw)
        _atomic_write(control.anchor, _bytes({'schema_version': 1, 'sequence': sequence,
                                            'journal_sha256': hashlib.sha256(raw).hexdigest()}))
        control.read()
        return {'revoked': True, 'already_revoked': False, 'sequence': sequence}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Private local library lifecycle; never deletes content.')
    parser.add_argument('action', choices=['initialize', 'revoke'])
    parser.add_argument('--journal', required=True)
    parser.add_argument('--anchor', required=True)
    parser.add_argument('--lock', required=True)
    parser.add_argument('--library-id')
    parser.add_argument('--request-ref')
    args = parser.parse_args()
    try:
        if args.action == 'initialize':
            initialize(args.journal, args.anchor, args.lock)
            result = {'initialized': True, 'real_content_processed': False}
        else:
            if not args.library_id or not args.request_ref:
                raise ControlUnavailable()
            result = revoke(Revocations(args.journal, args.anchor, args.lock), args.library_id, args.request_ref)
        print(json.dumps(result))
    except Exception:
        print(json.dumps({'success': False, 'error': 'lifecycle_control_unavailable'}))
        raise SystemExit(1)
