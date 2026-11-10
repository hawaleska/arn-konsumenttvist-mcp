"""Only invented data. Actual six tool bodies run with local client and synthetic admission."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys

import pytest
import requests

from arn_library_client import LibraryClient, LibraryUnavailable, content_sha256, SOURCE
from arn_public_responses import TOOLS, public_tool_response
from conftest import ROOT, load_tools, Registry, License
from library_lifecycle import initialize


def control_args(folder):
    journal = folder / 'control/revocations.json'
    anchor = folder / 'trust/anchor.json'
    lock = folder / 'control/readers.lock'
    initialize(journal, anchor, lock)
    return dict(revocations_path=journal, revocation_anchor_path=anchor, revocation_lock_path=lock)


def existing_control(client):
    return dict(revocations_path=client.revocations.journal, revocation_anchor_path=client.revocations.anchor,
                revocation_lock_path=client.revocations.lock)


def record(i=1, **changes):
    result = dict(library_id=f'BIB-TEST-{i}', version=1, date='2026-01-01', category='El',
                outcome='bifall', summary='Syntetisk tvist om fiktiv robot och garanti.',
                facts='ENDAST PÅHITTAT: En robot slutade fungera efter leverans.',
                reasoning='Testresonemang: felet fanns vid leveransen och avhjälpande uteblev.',
                disposition='Testutfall: återbetalning mot återlämnande.',
                companies=['Fiktiv Robotbutik AB'], tags=['robot', 'garanti'], synthetic=True)
    result.update(changes)
    return result


def approve(row, **changes):
    result = dict(library_id=row['library_id'], content_sha256=content_sha256(row),
                status='approved', reviewer='SYNTHETIC TEST REVIEWER',
                reviewed_at='2026-11-10T00:00:00Z', legal_review='approved',
                identifiability_review='approved', legal_fidelity_review='approved')
    result.update(changes)
    return result


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('Unexpected network/PDF/live-client use')
    monkeypatch.setattr(requests.sessions.Session, 'request', forbidden)
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    monkeypatch.setattr(socket, 'getaddrinfo', forbidden)
    import arn_client, common_cases
    monkeypatch.setattr(arn_client, 'PdfReader', forbidden)
    monkeypatch.setattr(arn_client.ARNClient, '__init__', forbidden)
    monkeypatch.setattr(common_cases.ARNCommonCases, 'search', forbidden)


@pytest.fixture
def library(tmp_path):
    state = control_args(tmp_path)
    def build(rows=None, approvals=None, allow=True):
        rows = [record()] if rows is None else rows
        approvals = [approve(r) for r in rows] if approvals is None else approvals
        data = tmp_path / 'content/library.json'; control = tmp_path / 'content/approvals.json'
        data.parent.mkdir(exist_ok=True)
        data.write_text(json.dumps({'schema_version': 1, 'records': rows}, ensure_ascii=False), encoding='utf-8')
        control.write_text(json.dumps({'schema_version': 1, 'approvals': approvals}), encoding='utf-8')
        return LibraryClient(data, control, hashlib.sha256(control.read_bytes()).hexdigest(),
                             allow_synthetic=allow, **state)
    return build


ARGS = {'arn_search': {'query': 'robot'}, 'arn_get_decision': {'case_number': 'BIB-TEST-1'},
        'arn_search_and_read': {'query': 'robot'}, 'arn_search_company': {'company': 'Fiktiv Robotbutik AB'},
        'arn_search_company_and_read': {'company': 'Fiktiv Robotbutik AB'},
        'arn_similar_cases': {'problem': 'trasig robot'}}


@pytest.mark.parametrize('name', sorted(TOOLS))
def test_all_six_real_tool_bodies_use_only_library_and_charge_once(library, name):
    events = []; client = library(); license = License(events)
    tools = load_tools(Registry(), client, license)
    result = tools[name](**ARGS[name])
    assert events == ['consume']
    rows = [result['results']] if name == 'arn_get_decision' else result.get('decisions', result.get('results'))
    assert len(rows) == 1 and rows[0]['case_number'] == 'BIB-TEST-1'
    assert rows[0]['source'] == SOURCE + ':BIB-TEST-1:v1'
    assert result['coverage']['mode'] == 'reviewed_library_only'
    assert 'file_id' not in rows[0] and 'xsessiontag' not in rows[0]
    if name == 'arn_similar_cases':
        assert result['common_cases'] == []


@pytest.mark.parametrize('name', sorted(TOOLS))
def test_denied_quota_does_not_even_read_library(library, name, monkeypatch):
    client = library(); events = []; license = License(events); license.allowed = False
    monkeypatch.setattr(client, '_records', lambda: pytest.fail('Read before admission'))
    result = load_tools(Registry(), client, license)[name](**ARGS[name])
    assert result['error'] == 'payment_required' and events == ['consume']


@pytest.mark.parametrize('change', [
    {'status': 'draft'}, {'status': True}, {'reviewer': ''}, {'reviewed_at': '2026-11-10'},
    {'content_sha256': '0' * 64}, {'identifiability_review': 'unknown'},
    {'legal_review': 'pending'}, {'legal_fidelity_review': 'pending'}, {'extra': 'hidden'},
])
def test_invalid_approval_not_exposed_by_search_read_or_similarity(library, change):
    row = record(); a = approve(row); a.update(change)
    client = library([row], [a])
    assert client.search('') == [] and client.similar_cases('robot')['results'] == []
    with pytest.raises(LibraryUnavailable):
        client.get_decision(row['library_id'])


def test_missing_approval_and_unreviewed_row_cannot_piggyback(library):
    rows = [record(), record(2)]
    client = library(rows, [approve(rows[0])])
    assert [r['case_number'] for r in client.search('')] == ['BIB-TEST-1']
    with pytest.raises(LibraryUnavailable): client.get_decision('BIB-TEST-2')


@pytest.mark.parametrize('name', sorted(TOOLS))
def test_all_six_exclude_unapproved_rows(library, name):
    client = library([record()], []); events = []
    tools = load_tools(Registry(), client, License(events))
    if name == 'arn_get_decision':
        from mcp.server.mcpserver.exceptions import ToolError
        with pytest.raises(ToolError): tools[name](**ARGS[name])
    else:
        result = tools[name](**ARGS[name])
        assert result.get('decisions', result.get('results')) == []
    assert events == ['consume']


@pytest.mark.parametrize('duplicate', ['record', 'approval'])
def test_duplicate_ids_fail_closed(library, duplicate):
    row = record(); client = library([row, row] if duplicate == 'record' else [row],
                                    [approve(row), approve(row)] if duplicate == 'approval' else [approve(row)])
    assert client.search('') == []


@pytest.mark.parametrize('change', [{'original_url': 'https://arn.example.invalid'},
                                 {'reasoning': ''}, {'version': True}, {'date': 'not-a-date'},
                                 {'synthetic': 'false'}, {'companies': 'not-a-list'}])
def test_unapproved_schema_or_content_invalid_even_with_matching_hash(library, change):
    row = record(); row.update(change)
    assert library([row]).search('') == []


def test_modification_after_approval_and_revocation_fail_closed(library):
    client = library(); raw = json.loads(client.library_path.read_text(encoding='utf-8'))
    raw['records'][0]['reasoning'] += ' TAMPERED'
    client.library_path.write_text(json.dumps(raw), encoding='utf-8')
    assert client.search('') == []
    client.approvals_path.write_text('{"schema_version":1,"approvals":[]}', encoding='utf-8')
    with pytest.raises(LibraryUnavailable): client.search('')


def test_approval_pin_required_and_corrupt_file_no_details(library):
    client = library()
    with pytest.raises(LibraryUnavailable) as err:
        LibraryClient(client.library_path, client.approvals_path, '', **existing_control(client))
    assert str(client.library_path) not in str(err.value)
    client.library_path.write_text('{"schema_version":1,"schema_version":1,"records":[]}', encoding='utf-8')
    with pytest.raises(LibraryUnavailable): client.search('')


def test_synthetic_records_need_explicit_local_opt_in(library):
    assert library(allow=False).search('') == []


def test_packaged_examples_and_empty_default_are_safe(monkeypatch, tmp_path):
    state = control_args(tmp_path)
    folder = ROOT / 'library'
    expected = '803b73bb586e2600a24b583e11c7f7d35ff8f9f0e140bcdc51dbda12e9e0de1c'
    client = LibraryClient(folder / 'synthetic-example.json', folder / 'synthetic-approvals.json',
                           expected, allow_synthetic=True, **state)
    assert len(client.search('robot')) == 5
    assert LibraryClient(folder / 'synthetic-example.json', folder / 'synthetic-approvals.json', expected, **state).search('') == []
    for key in ('ARN_LIBRARY_PATH', 'ARN_LIBRARY_APPROVALS', 'ARN_LIBRARY_ALLOW_SYNTHETIC'):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv('ARN_LIBRARY_APPROVALS_SHA256', '6f3f4d6afe1df639c5f6e222fca2471ad844f22c0b4376980609c8e5ca8fe1e3')
    for env, key in [('ARN_LIBRARY_REVOCATIONS', 'revocations_path'),
                     ('ARN_LIBRARY_REVOCATION_ANCHOR', 'revocation_anchor_path'),
                     ('ARN_LIBRARY_REVOCATION_LOCK', 'revocation_lock_path')]:
        monkeypatch.setenv(env, str(state[key]))
    assert LibraryClient.from_environment().search('') == []


def test_growth_filters_and_complete_reviewed_text(library):
    rows = [record(i) for i in range(1, 16)]
    rows[1].update(category='Motor', outcome='avslag', date='2025-03-04')
    client = library(rows)
    assert len(client.search('robot')) == 15
    assert len(client.search('robot', category='Motor', outcome='avslag', from_year='2025', to_year='2025')) == 1
    assert len(client.search('robot', category='elektronik')) == 14
    assert client.search('robot', from_year='2027') == []
    assert len(client.similar_cases('robot', max_results=3)['results']) == 3
    text = client.get_decision('BIB-TEST-1')['text']
    assert all(rows[0][f] in text for f in ('facts', 'reasoning', 'disposition'))
    assert len(client.search('BIB-TEST-1')) == 1
    assert client.search('nonexistent') == []


def test_growth_is_data_and_approval_update_without_server_code(library):
    client = library()
    rows = [record(), record(2)]
    client.library_path.write_text(json.dumps({'schema_version': 1, 'records': rows}), encoding='utf-8')
    assert len(client.search('robot')) == 1  # New content alone is never approved.
    client.approvals_path.write_text(json.dumps({'schema_version': 1, 'approvals': [approve(r) for r in rows]}), encoding='utf-8')
    with pytest.raises(LibraryUnavailable): client.search('robot')  # Old trust pin rejects changes.
    updated = LibraryClient(client.library_path, client.approvals_path,
                            hashlib.sha256(client.approvals_path.read_bytes()).hexdigest(),
                            allow_synthetic=True, **existing_control(client))
    assert len(updated.search('robot')) == 2


@pytest.mark.parametrize('args', [{'from_year': 'bad'}, {'from_year': '2027', 'to_year': '2025'}, {'outcome': 'bad'}])
def test_invalid_filters_never_broaden_scope(library, args):
    with pytest.raises(ValueError): library().search('', **args)


def test_no_document_handle_bypass(library):
    client = library()
    with pytest.raises(LibraryUnavailable):
        client.get_decision('2026-ORIGINAL', file_id='BIB-TEST-1', xsessiontag='https://example.invalid')
    assert client.get_decision('BIB-TEST-1', file_id='https://example.invalid')['case_number'] == 'BIB-TEST-1'


def test_scope_count_empty_and_unknown_are_truthful(library):
    client = library([], []); events = []; tools = load_tools(Registry(), client, License(events))
    result = tools['arn_search'](query='anything')
    assert result['count'] == 0 and result['coverage']['mode'] == 'reviewed_library_only'
    from mcp.server.mcpserver.exceptions import ToolError
    with pytest.raises(ToolError): tools['arn_get_decision'](case_number='BIB-MISSING')
    assert events == ['consume', 'consume']


def test_payment_files_and_all_tool_bodies_match_pinned_baseline():
    # Portable, frozen digests of revision 8125244, not a host-local source path.
    frozen = (ROOT / 'tests/library_contracts_8125244.json').read_bytes()
    assert hashlib.sha256(frozen).hexdigest() == 'd40582c04d0f4f889e82b97d5d918c9e26108d7289600f53692b15a755b28a3b'
    baseline = json.loads(frozen)
    assert baseline['revision'] == '812524461c3aef53e25295afda13247672801e81'
    for name in ('arn_license.py', 'arn_paypal_store.py', 'arn_auth.py'):
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == baseline['file_sha256'][name]
    current = ast.parse((ROOT / 'arn_mcp.py').read_text(encoding='utf-8'))
    names = TOOLS | {'arn_create_subscription', 'arn_cancel_subscription', 'consume_for_tool'}
    def functions(tree):
        return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names}
    b = functions(current)
    assert set(baseline['contracts']) == set(b) == names
    for name in names:
        assert hashlib.sha256(ast.dump(ast.Module(body=b[name].body, type_ignores=[])).encode()).hexdigest() == baseline['contracts'][name]['body_sha256']
        assert hashlib.sha256(ast.dump(b[name].args).encode()).hexdigest() == baseline['contracts'][name]['args_sha256']


def test_real_sdk_startup_lists_eight_tools_without_network_or_real_config(tmp_path):
    state = control_args(tmp_path)
    # All startup side effects are confined to this synthetic copy, with no .env copied.
    for file in ROOT.glob('*.py'): shutil.copyfile(file, tmp_path / file.name)
    shutil.copytree(ROOT / 'library', tmp_path / 'library')
    code = '''
import sys,socket
sys.path.insert(0,sys.argv[1])
def forbidden(*a,**k):raise AssertionError('External network forbidden')
socket.socket.connect=forbidden
socket.getaddrinfo=forbidden
import requests
requests.sessions.Session.request=forbidden
import arn_mcp as app
assert app.client.search('')==[]
# This SDK coroutine contains no awaits: execute the actual SDK conversion to
# completion without constructing Windows' network-dependent event-loop socketpair.
# A future SDK that suspends here fails this test rather than bypassing its work.
operation=app.server.list_tools()
try:
    operation.send(None)
except StopIteration as done:
    tools=done.value
else:
    operation.close()
    raise AssertionError('SDK list_tools unexpectedly requires an async runtime')
names={t.name for t in tools}
assert names=={'arn_search','arn_get_decision','arn_search_and_read','arn_search_company','arn_search_company_and_read','arn_similar_cases','arn_create_subscription','arn_cancel_subscription'}
filters={'category','outcome','from_year','to_year'}
expected={
 'arn_search':{'query'}|filters,
 'arn_get_decision':{'case_number'},
 'arn_search_and_read':{'query','max_results'}|filters,
 'arn_search_company':{'company','max_results'}|filters,
 'arn_search_company_and_read':{'company','max_results'}|filters,
 'arn_similar_cases':{'problem','max_results'}|filters,
 'arn_create_subscription':{'plan'},'arn_cancel_subscription':set()}
for t in tools:
    assert set(t.input_schema['properties'])==expected[t.name],t.name
    if t.name not in {'arn_create_subscription','arn_cancel_subscription'}:
        assert 'bibliotek' in t.description
print('LOCAL_LIBRARY_SDK_EIGHT_TOOLS_PASS')
'''
    env = {k: os.environ[k] for k in ('SYSTEMROOT', 'WINDIR', 'PATH', 'TEMP', 'TMP') if k in os.environ}
    env.update(ARN_D1_API_URL='https://synthetic-backend.invalid', ARN_D1_API_SECRET='synthetic',
               PAYPAL_ENV='sandbox', PAYPAL_CLIENT_ID='synthetic', PAYPAL_CLIENT_SECRET='synthetic',
               PAYPAL_WEBHOOK_ID='synthetic', PAYPAL_MONTHLY_PLAN_ID='synthetic-month',
               PAYPAL_YEARLY_PLAN_ID='synthetic-year',
               ARN_LIBRARY_APPROVALS_SHA256=hashlib.sha256((tmp_path/'library/approvals.json').read_bytes()).hexdigest())
    env.update(ARN_LIBRARY_REVOCATIONS=str(state['revocations_path']),
               ARN_LIBRARY_REVOCATION_ANCHOR=str(state['revocation_anchor_path']),
               ARN_LIBRARY_REVOCATION_LOCK=str(state['revocation_lock_path']))
    result = subprocess.run([sys.executable, '-I', '-B', '-c', code, str(tmp_path)],
                            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'LOCAL_LIBRARY_SDK_EIGHT_TOOLS_PASS' in result.stdout
