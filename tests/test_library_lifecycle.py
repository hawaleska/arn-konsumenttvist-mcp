"""Synthetic lifecycle, old-content restore and independent latest-state anchor."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest

from arn_library_client import LibraryClient, LibraryUnavailable
from arn_public_responses import TOOLS
from conftest import ROOT, load_tools, Registry, License
from library_lifecycle import initialize, revoke, ControlUnavailable, Revocations
from test_reviewed_library import (library, no_network, record, approve, ARGS, existing_control)

CASE = 'CASE-000000000000000000000001'


def visible(tools, name):
    from mcp.server.mcpserver.exceptions import ToolError
    if name == 'arn_get_decision':
        with pytest.raises(ToolError): tools[name](**ARGS[name])
    else:
        result = tools[name](**ARGS[name])
        assert result.get('decisions', result.get('results')) == []


@pytest.mark.parametrize('name', sorted(TOOLS))
def test_revoke_hides_post_from_every_tool_and_keeps_quota(library, name):
    client = library(); events = []; tools = load_tools(Registry(), client, License(events))
    assert revoke(client.revocations, 'BIB-TEST-1', CASE)['revoked']
    visible(tools, name)
    assert events == ['consume']


@pytest.mark.parametrize('name', sorted(TOOLS))
def test_older_content_approval_and_pin_restore_cannot_reactivate(library, name):
    client = library()
    old_content = client.library_path.read_bytes()
    old_approval = client.approvals_path.read_bytes()
    old_pin = client.approvals_sha256
    revoke(client.revocations, 'BIB-TEST-1', CASE)
    # Full ordinary content bundle rollback, including its original approval pin.
    client.library_path.write_bytes(old_content)
    client.approvals_path.write_bytes(old_approval)
    restored = LibraryClient(client.library_path, client.approvals_path, old_pin,
                             allow_synthetic=True, **existing_control(client))
    visible(load_tools(Registry(), restored, License([])), name)


def test_new_version_and_approval_do_not_lift_tombstone(library):
    client = library(); revoke(client.revocations, 'BIB-TEST-1', CASE)
    row = record(version=2); row['summary'] += ' Ny syntetisk version.'
    client.library_path.write_text(json.dumps({'schema_version': 1, 'records': [row]}), encoding='utf-8')
    client.approvals_path.write_text(json.dumps({'schema_version': 1, 'approvals': [approve(row)]}), encoding='utf-8')
    newer = LibraryClient(client.library_path, client.approvals_path,
                          hashlib.sha256(client.approvals_path.read_bytes()).hexdigest(),
                          allow_synthetic=True, **existing_control(client))
    assert newer.search('') == []


def test_revocation_is_idempotent_minimal_and_preserves_other_post(library):
    client = library([record(), record(2)])
    assert not revoke(client.revocations, 'BIB-TEST-1', CASE)['already_revoked']
    first = client.revocations.journal.read_bytes()
    assert revoke(client.revocations, 'BIB-TEST-1', CASE)['already_revoked']
    assert client.revocations.journal.read_bytes() == first
    journal = json.loads(first)
    assert set(journal['events'][0]) == {'sequence', 'library_id', 'request_ref', 'revoked_at'}
    assert 'Fiktiv' not in first.decode() and '@' not in first.decode() and 'reasoning' not in first.decode()
    assert [r['case_number'] for r in client.search('robot')] == ['BIB-TEST-2']
    with pytest.raises(ControlUnavailable): revoke(client.revocations, 'BIB-TEST-2', 'person@example.invalid')


@pytest.mark.parametrize('damage', ['old_journal', 'old_anchor', 'missing_journal',
                                   'missing_anchor', 'missing_lock', 'modified_journal'])
def test_bad_or_restored_control_state_fails_closed(library, damage):
    client = library(); old_journal = client.revocations.journal.read_bytes()
    old_anchor = client.revocations.anchor.read_bytes()
    revoke(client.revocations, 'BIB-TEST-1', CASE)
    if damage == 'old_journal': client.revocations.journal.write_bytes(old_journal)
    if damage == 'old_anchor': client.revocations.anchor.write_bytes(old_anchor)
    if damage == 'missing_journal': client.revocations.journal.unlink()
    if damage == 'missing_anchor': client.revocations.anchor.unlink()
    if damage == 'missing_lock': client.revocations.lock.unlink()
    if damage == 'modified_journal': client.revocations.journal.write_text('{"schema_version":1,"events":[]}', encoding='utf-8')
    with pytest.raises(LibraryUnavailable): client.search('')
    with pytest.raises(LibraryUnavailable): client.get_decision('BIB-TEST-1')
    with pytest.raises(LibraryUnavailable): client.similar_cases('robot')


def test_control_not_optional_or_silently_initialized(library):
    client = library()
    with pytest.raises(LibraryUnavailable):
        LibraryClient(client.library_path, client.approvals_path, client.approvals_sha256, allow_synthetic=True)
    with pytest.raises(ControlUnavailable):
        initialize(client.revocations.journal, client.revocations.anchor, client.revocations.lock)
    with pytest.raises(ControlUnavailable):
        Revocations(client.revocations.journal, client.revocations.journal.parent/'bad-anchor', client.revocations.lock)


def test_control_paths_cannot_be_put_in_ordinary_content_backup(library):
    client = library()
    for field in ('revocations_path', 'revocation_anchor_path', 'revocation_lock_path'):
        args = existing_control(client)
        args[field] = client.library_path.parent / ('bad-' + field)
        with pytest.raises(LibraryUnavailable):
            LibraryClient(client.library_path, client.approvals_path, client.approvals_sha256,
                          allow_synthetic=True, **args)


def test_interrupted_journal_anchor_commit_is_not_success(library, monkeypatch):
    import library_lifecycle as lifecycle
    client = library(); original = lifecycle._atomic_write
    def interrupted(path, data):
        if Path(path) == client.revocations.anchor:
            raise OSError('synthetic interrupted commit')
        original(path, data)
    monkeypatch.setattr(lifecycle, '_atomic_write', interrupted)
    with pytest.raises(OSError): revoke(client.revocations, 'BIB-TEST-1', CASE)
    with pytest.raises(LibraryUnavailable): client.search('')
    assert len(json.loads(client.revocations.journal.read_bytes())['events']) == 1


def test_parallel_duplicate_revocation_is_one_event(library):
    client = library()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: revoke(client.revocations, 'BIB-TEST-1', CASE), range(8)))
    assert sum(not r['already_revoked'] for r in results) == 1
    assert len(client.revocations.read()[0]['events']) == 1


def test_cross_process_writer_waits_for_reader_then_restart_preserves_revocation(library):
    client = library()
    code = '''
import sys,json
sys.path.insert(0,sys.argv[1])
from library_lifecycle import Revocations,revoke
print('READY',flush=True)
print(json.dumps(revoke(Revocations(*sys.argv[2:5]),'BIB-TEST-1',sys.argv[5])),flush=True)
'''
    with client.exposure_guard():
        proc = subprocess.Popen([sys.executable, '-I', '-B', '-c', code, str(ROOT),
                                 str(client.revocations.journal), str(client.revocations.anchor),
                                 str(client.revocations.lock), CASE], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        try:
            assert proc.stdout.readline().strip() == 'READY'
            assert proc.poll() is None
            assert client.get_decision('BIB-TEST-1')['case_number'] == 'BIB-TEST-1'
        except BaseException:
            proc.kill(); proc.communicate(); raise
    out, err = proc.communicate(timeout=10)
    assert proc.returncode == 0, err
    assert json.loads(out)['revoked']
    restored = LibraryClient(client.library_path, client.approvals_path, client.approvals_sha256,
                             allow_synthetic=True, **existing_control(client))
    assert restored.search('') == []


def test_public_serialization_is_inside_exposure_guard(library, monkeypatch):
    import arn_public_responses as responses
    client = library(); tools = load_tools(Registry(), client, License([]))
    original = responses.public_tool_response
    def checked(*args, **kwargs):
        assert client._exposure.depth == 1
        return original(*args, **kwargs)
    monkeypatch.setattr(responses, 'public_tool_response', checked)
    assert tools['arn_search'](query='robot')['count'] == 1


@pytest.mark.skipif(os.name == 'nt', reason='POSIX mode preservation')
def test_posix_control_modes_not_weakened_by_commit(library):
    import stat
    client = library()
    client.revocations.journal.chmod(0o640)
    client.revocations.anchor.chmod(0o640)
    revoke(client.revocations, 'BIB-TEST-1', CASE)
    assert stat.S_IMODE(client.revocations.journal.stat().st_mode) == 0o640
    assert stat.S_IMODE(client.revocations.anchor.stat().st_mode) == 0o640
