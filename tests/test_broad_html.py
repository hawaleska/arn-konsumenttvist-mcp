"""Synthetic HTML and actual six tool bodies. No real network or PDF requests."""
import ast
import copy
import hashlib
from pathlib import Path

import pytest
import requests

from arn_html_search import (BroadHTMLClient, OfficialHTML, HTMLUnavailable, DATABASE,
                             OVERVIEW, case_control_id, _row, _minimized_excerpt, safe_source)
from arn_library_client import LibraryUnavailable
from arn_public_responses import public_decision
from library_lifecycle import revoke
from test_reviewed_library import library, no_network, existing_control, ARGS
from test_summary_compatibility import row, approval, build
from conftest import load_tools, Registry, License


class Source:
    def __init__(self, rows=None, fail=False):
        self.rows = rows if rows is not None else [_row('9999-90002', 'Fiktiv robot hade ett fel.', 'El', '2099-01-02')]
        self.calls = []
        self.fail = fail

    def search(self, *args):
        self.calls.append(args)
        if self.fail:
            raise HTMLUnavailable('synthetic upstream secret must not escape')
        return copy.deepcopy(self.rows), {'database': 'ok', 'latest_overview': 'ok'}


def broad(library, source=None, rows=None, enabled=True):
    rows = rows or []
    base = build(library, rows)
    return BroadHTMLClient(base.library_path, base.approvals_path, base.approvals_sha256,
                           allow_synthetic=True, source=source or Source(), enabled=enabled,
                           source_mode='official_html',
                           **existing_control(base))


@pytest.mark.parametrize('tool', sorted(ARGS))
def test_six_tools_use_broad_source_after_one_admission(library, tool):
    source = Source()
    client = broad(library, source)
    events = []
    tools = load_tools(Registry(), client, License(events))
    args = dict(ARGS[tool])
    if tool == 'arn_get_decision':
        args['case_number'] = '9999-90002'
    result = tools[tool](**args)
    records = [result['results']] if tool == 'arn_get_decision' else result.get('decisions', result.get('results'))
    assert len(records) == 1
    assert records[0]['case_number'] == '9999-90002'
    assert records[0]['read_status'] == 'not_locally_approved'
    assert records[0]['source'] == DATABASE
    assert records[0]['source_link_kind'] == 'overview'
    assert 'hela beslutet' not in records[0].get('text', '')
    assert result['coverage']['mode'] == 'official_html_and_reviewed_library'
    assert events == ['consume']
    assert source.calls
    assert client._html_state.rows == {}  # request-local data discarded


def test_combined_call_reuses_request_local_excerpt_without_refetch(library):
    source = Source(); client = broad(library, source)
    load_tools(Registry(), client, License([]))['arn_search_and_read'](query='robot')
    assert len(source.calls) == 1


@pytest.mark.parametrize('tool', sorted(ARGS))
def test_denied_quota_never_reaches_html(library, tool):
    source = Source();client = broad(library, source);events=[];license = License(events);license.allowed=False
    result = load_tools(Registry(), client, license)[tool](**ARGS[tool])
    assert result['error'] == 'payment_required'
    assert source.calls == [] and events == ['consume']


def test_unknown_company_is_a_source_text_query_not_a_verified_company_match(library):
    source=Source([]);client=broad(library,source)
    result=load_tools(Registry(),client,License([]))['arn_search_company'](company='Syntetiskt Ej Finns AB')
    assert result['count']==0 and source.calls[0][0]=='Syntetiskt Ej Finns AB'


def test_similar_cases_keeps_relevant_word_stems_instead_of_false_empty(library):
    source=Source([_row('9999-90002','En fiktiv flygresa blev inställd.')])
    client=broad(library,source)
    result=client.similar_cases('flyg')
    assert result['count']==1 and result['results'][0]['score']>0


def test_empty_results_and_source_failure_are_distinct_and_neutral(library):
    client=broad(library,Source([]));assert client.search('syntetiskt')==[]
    client.html=Source(fail=True)
    with pytest.raises(Exception) as exc:
        load_tools(Registry(),client,License([]))['arn_search'](query='syntetiskt')
    assert 'upstream secret' not in str(exc.value)


def test_disabled_candidate_never_claims_broad_coverage(library):
    source=Source();client=broad(library,source,enabled=False)
    with pytest.raises(HTMLUnavailable):client.search('robot')
    assert source.calls==[]


@pytest.mark.parametrize('query',['fiktiv@example.invalid','personnummer: 19990101-1234','990101-1234'])
def test_contact_queries_rejected_before_external_transfer(library,query):
    source=Source();client=broad(library,source)
    with pytest.raises(ValueError):client.search(query)
    assert source.calls==[]


def test_approved_local_read_stays_hash_bound_and_distinct(library):
    value=row(original_case_number='9999-90001',official_source_url=OVERVIEW)
    client=broad(library,Source([_row('9999-90001','Fiktiv robot.')]),[value])
    result=client.search('robot')[0]
    assert result['read_status']=='locally_approved'
    assert 'inte hela ARN-beslutet' in client.get_decision('9999-90001')['text']
    saved=client.library_path.read_bytes()
    revoke(client.revocations,value['library_id'],'CASE-000000000000000000000001')
    client.library_path.write_bytes(saved)
    assert client.search('robot')==[]
    with pytest.raises(LibraryUnavailable):client.get_decision('9999-90001')


def test_unreviewed_source_can_be_revoked_with_existing_control(library):
    client=broad(library)
    assert client.search('robot')
    revoke(client.revocations,case_control_id('9999-90002'),'CASE-000000000000000000000002')
    assert client.search('robot')==[]
    with pytest.raises(LibraryUnavailable):client.get_decision('9999-90002')


def test_missing_old_library_tombstone_blocks_live_bypass(library):
    client=broad(library)
    revoke(client.revocations,'BIB-OLD-MISSING','CASE-000000000000000000000003')
    with pytest.raises(LibraryUnavailable):client.search('robot')


def test_tampered_approval_control_blocks_live_search(library):
    source=Source();client=broad(library,source)
    client.approvals_path.write_text('{}',encoding='utf-8')
    with pytest.raises(LibraryUnavailable):client.search('robot')
    assert source.calls==[]


@pytest.mark.parametrize('text',['Konsumenten hade en demenssjukdom.',
                               'Konsumenten var misstänkt för bedrägeri.',
                               'Ett villkor hänvisar till penningtvättslagen.'])
def test_potential_sensitive_context_withheld_without_claiming_legal_classification(text):
    excerpt,risk=_minimized_excerpt(text)
    assert text not in excerpt and risk=='potential_sensitive_context'


def test_legal_abbreviations_retained_and_initials_minimized():
    text,risk=_minimized_excerpt('AA hade ett avtal. ARN har bedömt frågan enligt EU och NJA 2020 s. 1.')
    assert 'AA hade' not in text and 'konsumenten hade' in text
    assert 'ARN har' in text and 'EU' in text and 'NJA 2020' in text


@pytest.mark.parametrize('role', ['Flygbolaget', 'Företaget', 'Banken', 'Bolaget'])
def test_explicit_company_role_is_not_replaced_with_consumer(role):
    original = f'{role} A har utfört tjänsten. AA hade ett avtal enligt EU.'
    text, risk = _minimized_excerpt(original)
    assert f'{role} A har' in text
    assert f'{role} konsumenten' not in text
    assert 'AA hade' not in text and 'konsumenten hade' in text
    assert risk == 'none_detected_not_reviewed'


def index_client(library, rows, approvals=None):
    base = build(library, rows, approvals)
    return BroadHTMLClient(base.library_path, base.approvals_path, base.approvals_sha256,
                           allow_synthetic=True, enabled=True, source_mode='reviewed_index',
                           **existing_control(base))


@pytest.mark.parametrize('tool', sorted(ARGS))
def test_reviewed_index_six_tools_have_no_network_or_live_fallback(library, tool):
    # A post-construction source replacement is a hostile fallback attempt.
    # The reviewed-index path must still return only hash-approved library rows.
    value = row(companies=['Fiktiv Robotbutik AB'],
                summary='En trasig robot i ett syntetiskt ärende.',
                source_text='En trasig robot i ett syntetiskt ärende.')
    client = index_client(library, [value])
    hostile = Source([_row('9999-90002', 'Ogranskat liveutdrag om en robot.')])
    client.html = hostile
    events = []
    result = load_tools(Registry(), client, License(events))[tool](**ARGS[tool])
    values = [result['results']] if tool == 'arn_get_decision' else result.get('decisions', result.get('results'))
    assert len(values) == 1
    assert values[0]['read_status'] == 'locally_approved'
    assert values[0]['case_number'] == value.get('original_case_number', value['library_id'])
    assert values[0]['source'] != DATABASE
    assert hostile.calls == []
    assert result['coverage']['mode'] == 'reviewed_local_index'
    assert events == ['consume']


def test_reviewed_index_is_safe_default_when_mode_is_not_configured(library, monkeypatch):
    monkeypatch.delenv('ARN_BROAD_SOURCE_MODE', raising=False)
    base = build(library, [row()])
    client = BroadHTMLClient(base.library_path, base.approvals_path, base.approvals_sha256,
                             allow_synthetic=True, enabled=True, **existing_control(base))
    assert client.source_mode == 'reviewed_index'
    assert client.search('robot')[0]['read_status'] == 'locally_approved'


def test_nonblank_query_returns_only_exactly_approved_index_rows(library):
    approved = row(library_id='BIB-TEST-1', summary='Godkänt syntetiskt fall om robot.')
    pending = row(library_id='BIB-TEST-2', summary='Väntande syntetiskt fall om robot.')
    approvals = [approval(approved), {**approval(pending), 'status': 'pending'}]
    client = index_client(library, [approved, pending], approvals)
    hostile = Source([_row('9999-90003', 'Live text ska aldrig visas.')])
    client.html = hostile

    results = client.search('robot')

    assert [result['case_number'] for result in results] == ['BIB-TEST-1']
    assert results[0]['read_status'] == 'locally_approved'
    assert hostile.calls == []


def test_reviewed_index_direct_read_does_not_fallback_to_live_source(library):
    client = index_client(library, [row()])
    hostile = Source([_row('9999-90009', 'Unapproved live fallback text.')])
    client.html = hostile
    with pytest.raises(LibraryUnavailable):
        client.get_decision('9999-90009')
    assert hostile.calls == []


def test_reviewed_index_common_case_link_and_unknown_metadata(library):
    value = row(original_case_number='9999-90003',
                official_source_url='https://www.arn.se/vanligafall/1.1.-syntetiskt-fall/')
    client = index_client(library, [value])
    result = public_decision(client.get_decision('9999-90003'))
    assert result['source'] == value['official_source_url']
    assert result['source_link_kind'] == 'case_specific'
    assert result['source_kind'] == 'common_case_example'
    assert result['date'] == 'okänt'
    assert client.search('robot', outcome='bifall') == []
    assert client.search('robot', from_year='2020') == []


@pytest.mark.parametrize('change', [{'status':'pending'}, {'content_sha256':'0'*64},
                                  {'legal_review':'pending'}, {'publication_review':None}])
def test_reviewed_index_does_not_promote_staging_or_tampered_approval(library, change):
    value = row(); a = approval(value); a.update(change)
    client = index_client(library, [value], [a])
    assert client.search('robot') == []
    with pytest.raises(LibraryUnavailable):
        client.get_decision(value['library_id'])


def test_reviewed_index_revocation_blocks_search_and_direct_read(library):
    value = row(); client = index_client(library, [value])
    assert client.search('robot')
    revoke(client.revocations, value['library_id'], 'CASE-000000000000000000000005')
    assert client.search('robot') == []
    with pytest.raises(LibraryUnavailable):
        client.get_decision(value['library_id'])


def test_reviewed_index_forbids_injected_upstream_adapter(library):
    base = build(library, [row()])
    with pytest.raises(LibraryUnavailable):
        BroadHTMLClient(base.library_path, base.approvals_path, base.approvals_sha256,
                        source=Source(), source_mode='reviewed_index', **existing_control(base))


@pytest.mark.parametrize('url', ['https://www.arn.se/vanligafall/source.pdf',
                               'https://www.arn.se/vanligafall/a/?fileId=1',
                               'https://example.invalid/vanligafall/a/'])
def test_reviewed_index_rejects_invalid_common_case_sources(library, url):
    value = row(original_case_number='9999-90003', official_source_url=url)
    client = index_client(library, [value])
    assert client.search('robot') == []


def test_reviewed_index_changed_content_cannot_reuse_approval(library):
    value = row(); a = approval(value)
    changed = {**value, 'source_text':'A changed synthetic text.'}
    assert index_client(library, [changed], [a]).search('robot') == []


def test_serializer_never_exposes_unreviewed_fulltext_or_private_handles():
    value={**_row('9999-90002','Fiktivt fel.'),'text':'RAW_UNREVIEWED_TEXT',
           'pdf_url':'https://adokweb.arn.se/secret.pdf','xsessiontag':'SECRET'}
    result=public_decision(value)
    assert 'RAW_UNREVIEWED_TEXT' not in str(result) and 'SECRET' not in str(result)
    assert result['read_status']=='not_locally_approved'


class Response:
    def __init__(self, text='', status=200, headers=None):
        self.body=text.encode('utf-8');self.status_code=status
        self.headers=headers or {'Content-Type':'text/html; charset=UTF-8"'};self.closed=False
    def __enter__(self):return self
    def __exit__(self,*args):self.closed=True
    def raise_for_status(self):
        if self.status_code>=400:raise requests.HTTPError('synthetic error')
    def iter_content(self,size):
        for i in range(0,len(self.body),size):yield self.body[i:i+size]


class Session:
    def __init__(self,responses):self.responses=list(responses);self.calls=[];self.headers={};self.closed=False
    def __enter__(self):return self
    def __exit__(self,*args):self.closed=True
    def request(self,method,url,**kwargs):
        self.calls.append((method,url,kwargs));return self.responses.pop(0)


FORM='''<form action="/digiforms/htmlViewer?xsessiontag=SYNTHETIC">
<input id="input-search-referatwebb" name="q"><button id="btn-search" onclick="submitCmd('cmd')"></button></form>'''
RESULT=FORM+'''<div class="case-container"><fieldset>9999-90002 2099-01-02 El
Fiktiv robot hade fel.<button onclick="open('secret.pdf')">Hela beslutet</button></fieldset></div>'''
LATEST='''<h1>Vägledande beslut</h1><h3>El, beslut 2099-01-02</h3>
<p>Fiktiv robot hade fel.</p><p><a href="/pdfs/fiktivt.pdf">Referat 9999-90003</a></p><hr>'''


def test_real_form_parser_only_requests_html_and_parses_unknowns_honestly():
    responses=[Response(FORM),Response(RESULT),Response(LATEST)];session=Session(responses)
    source=OfficialHTML(lambda:session, robots_check=lambda *_: True, common_catalog=());rows,states=source.search('robot')
    assert {r['case_number'] for r in rows}=={'9999-90002','9999-90003'}
    assert all(r['source_link_kind']=='overview' for r in rows)
    assert all('Hela beslutet' not in r['summary'] for r in rows)
    assert len(session.calls)==3 and session.calls[1][2]['data']['q']=='robot'
    assert all('pdf' not in url for _,url,_ in session.calls)
    assert session.closed and all(r.closed for r in responses)
    assert states=={'database':'ok','latest_overview':'ok'}


@pytest.mark.parametrize('target',['https://example.invalid/','https://adokweb.arn.se/file.pdf',
                                   'https://adokweb.arn.se/digiforms/sessionInitializer?fileId=1'])
def test_redirect_to_pdf_or_other_host_rejected_before_fetch(target):
    response=Response(status=302,headers={'Location':target});s=Session([response])
    with pytest.raises(HTMLUnavailable):OfficialHTML()._html(s,'GET',DATABASE)
    assert len(s.calls)==1 and response.closed


def test_ordinary_html_bootstrap_is_allowed_but_not_file_download():
    responses=[Response(status=302,headers={'Location':'/digiforms/sessionInitializer?processName=ARN_Referatwebb_process'}),
               Response(status=302,headers={'Location':'/digiforms/sessionInitializer?xsessiontag=SYNTHETIC'}),
               Response(status=302,headers={'Location':'/digiforms/htmlViewer?xsessiontag=SYNTHETIC'}),Response(FORM)]
    session=Session(responses)
    soup,url=OfficialHTML()._html(session,'GET',DATABASE)
    assert soup.select_one('#input-search-referatwebb') is not None and len(session.calls)==4
    assert all(r.closed for r in responses)
    assert not OfficialHTML._allowed(url+'&fileId=1')


@pytest.mark.parametrize('response',[Response('binary',headers={'Content-Type':'application/pdf'}),
                                   Response('x'*(2*1024*1024+1)),Response(status=403)])
def test_type_size_and_access_errors_close_response_without_bypass(response):
    s=Session([response])
    with pytest.raises((HTMLUnavailable,requests.HTTPError)):OfficialHTML()._html(s,'GET',DATABASE)
    assert response.closed and len(s.calls)==1


def test_partial_source_failure_is_visible():
    session=Session([Response(status=403),Response(LATEST)])
    rows,states=OfficialHTML(lambda:session, robots_check=lambda *_: True, common_catalog=()).search('robot')
    assert rows and states=={'database':'unavailable','latest_overview':'ok'}


def test_all_sources_failed_is_not_false_empty_result():
    with pytest.raises(HTMLUnavailable):OfficialHTML(lambda:Session([Response(status=403),Response(status=403)]), robots_check=lambda *_: True, common_catalog=()).search('robot')


def test_case_specific_html_source_and_missing_fields():
    html=LATEST.replace('/pdfs/fiktivt.pdf','/om-arn/vagledande-beslut/fiktiv/')
    rows=OfficialHTML().overview(Session([Response(html)]),'robot')
    assert rows[0]['source_link_kind']=='case_specific' and safe_source(rows[0]['source'])
    r=_row('9999-90009','Fiktiv rättsfråga.')
    assert r['date']=='okänt' and r['category']=='okänd'


def test_eight_argument_contracts_and_all_payment_functions_unchanged():
    from test_consumer_composition import functions
    root=Path(__file__).resolve().parents[1]
    before=functions(root/'baseline/installed-main.py');after=functions(root/'arn_mcp.py')
    for name in before:
        old_args=before[name].args.args
        new_args=after[name].args.args
        old_names=[arg.arg for arg in old_args]
        new_names=[arg.arg for arg in new_args]
        assert new_names[:len(old_names)]==old_names
        assert new_names[len(old_names):]==(['cursor'] if name=='arn_search' else [])
        if name=='arn_search':
            assert after[name].args.defaults[-1].value==''
    # Independent 1.0.4 function-body hashes, not a newly generated fixture.
    import json
    baseline=json.loads((root/'tests/production_contracts_20261112.json').read_text(encoding='utf-8'))
    # Existing full body/contract tests also run; only six descriptions changed.
    assert baseline['file_sha256']['arn_auth.py']==hashlib.sha256((root/'arn_auth.py').read_bytes()).hexdigest()


def test_robots_disallow_prevents_database_request_but_keeps_honest_overview():
    denied=Response('User-agent: *\nDisallow: /\n',headers={'Content-Type':'text/plain'})
    allowed=Response('',headers={'Content-Type':'text/plain'})
    session=Session([denied,allowed,Response(LATEST)])
    rows,states=OfficialHTML(lambda:session,common_catalog=()).search('robot')
    assert rows and states=={'database':'disallowed_by_robots','latest_overview':'ok'}
    assert session.calls[0][1]=='https://adokweb.arn.se/robots.txt'
    assert session.calls[0][2]['headers']['Accept']=='text/plain, */*'
    assert not any(url==DATABASE or '/digiforms/' in url for _,url,_ in session.calls)
    assert denied.closed and allowed.closed


def test_robots_unverifiable_cannot_be_bypassed():
    session=Session([Response(status=403),Response(status=403)])
    with pytest.raises(HTMLUnavailable):OfficialHTML(lambda:session,common_catalog=()).search('robot')
    assert all(url.endswith('/robots.txt') for _,url,_ in session.calls)


def make_catalog(tmp_path, changes=None, extra=None):
    import json
    from arn_html_search import CommonCaseCatalog
    row={k:v for k,v in _row('9999-90008','Fiktiv cykel med fel.').items()
         if k not in {'file_id','xsessiontag'}}
    row.update(source='https://www.arn.se/vanligafall/1.1.-fiktiv-cykel/',
               source_kind='common_case_example',source_link_kind='case_specific',title='Fiktiv cykel')
    row.update(changes or {})
    data={'schema_version':1,'source_kind':'common_case_examples',
          'source_review':'official_individual_html_verified',
          'legal_status':'local_candidate_not_approved_for_public_deployment',
          'source_checked_at':'2026-11-13','records':[row]}
    if extra:data['records'].append(dict(row))
    path=tmp_path/'common.json';path.write_text(json.dumps(data),encoding='utf-8')
    return CommonCaseCatalog(path,hashlib.sha256(path.read_bytes()).hexdigest())


def test_verified_common_snapshot_is_searchable_without_remote_access(tmp_path):
    catalog=make_catalog(tmp_path)
    session=Session([])
    rows,states=OfficialHTML(lambda:session,robots_check=lambda *_:False,
                             common_catalog=catalog).search('cykel')
    assert len(rows)==1 and rows[0]['source_kind']=='common_case_example'
    assert rows[0]['read_status']=='not_locally_approved'
    assert rows[0]['source_checked_at']=='2026-11-13'
    assert states['common_case_examples']=='ok' and session.calls==[]
    result=public_decision(rows[0])
    assert result['source_kind']=='common_case_example' and result['source_link_kind']=='case_specific'


@pytest.mark.parametrize('changes',[
    {'read_status':'locally_approved'}, {'text':'UNREVIEWED FULLTEXT'},
    {'source':'https://www.arn.se/globalassets/secret.pdf'},
    {'source_kind':'guiding_summary'}])
def test_catalog_cannot_promote_unreviewed_text_or_untrusted_source(tmp_path,changes):
    catalog=make_catalog(tmp_path,changes)
    with pytest.raises(LibraryUnavailable):catalog.search('')


def test_catalog_hash_failure_stops_before_any_network(tmp_path):
    catalog=make_catalog(tmp_path);catalog.path.write_text('{}',encoding='utf-8')
    session=Session([])
    with pytest.raises(LibraryUnavailable):OfficialHTML(lambda:session,common_catalog=catalog).search('')
    assert session.calls==[]


def test_exact_common_reference_does_not_fetch_whole_overview(tmp_path):
    catalog=make_catalog(tmp_path);session=Session([])
    rows,states=OfficialHTML(lambda:session,common_catalog=catalog).search('9999-90008')
    assert len(rows)==1 and states['latest_overview']=='not_consulted' and session.calls==[]


def test_catalog_duplicate_reference_fails_closed(tmp_path):
    with pytest.raises(LibraryUnavailable):make_catalog(tmp_path,extra=True).search('')


def test_common_result_deduplicates_and_never_replaces_guiding_source(library):
    common={**_row('9999-90002','Fiktiv robot.'),'source_kind':'common_case_example',
            'source':'https://www.arn.se/vanligafall/fiktiv/'}
    guiding=_row('9999-90002','Fiktiv robot.',source=OVERVIEW)
    client=broad(library,Source([guiding,common]))
    rows=client.search('robot')
    assert len(rows)==1 and rows[0]['source_kind']=='guiding_summary'
    revoke(client.revocations,case_control_id('9999-90002'),'CASE-000000000000000000000004')
    assert client.search('robot')==[]


def test_withheld_context_is_not_a_hidden_search_index():
    html='''<h1>Vägledande beslut</h1><h3>Bank, beslut2099-01-02</h3>
    <p>Konsumenten hade en demenssjukdom.</p>
    <p><a href="/pdfs/fiktivt.pdf">Referat 9999-90002</a></p><hr>'''
    source=OfficialHTML(common_catalog=())
    assert source.overview(Session([Response(html)]),'demens')==[]
    rows=source.overview(Session([Response(html)]),'9999-90002')
    assert len(rows)==1 and 'demens' not in rows[0]['summary']


def test_reviewed_index_search_uses_relevance_sorted_twenty_item_cursor_pages(library):
    values=[]
    for i in range(25):
        values.append(row(library_id=f'BIB-SYNTH-PAGE-{i:03d}',
                          original_case_number=f'9999-{i:05d}',
                          official_source_url=OVERVIEW,
                          summary=f'Fiktivt robotärende {i}.',
                          source_text=f'Fiktivt robotärende {i}.'))
    client=index_client(library,values)
    first=client.search('robot')
    page_meta=client._html_state.page.copy()
    assert len(first)==20 and page_meta['total_matches']==25
    assert page_meta['result_limit']==20 and page_meta['has_more'] is True
    assert page_meta['next_cursor']
    second=client.search('robot',cursor=page_meta['next_cursor'])
    second_meta=client._html_state.page.copy()
    assert len(second)==5 and second_meta['has_more'] is False
    all_refs=[r['case_number'] for r in first+second]
    assert len(all_refs)==25 and len(set(all_refs))==25
    assert all_refs==sorted(all_refs)  # equal relevance; stable library-ID tie-break


def test_blank_and_changed_or_invalid_search_cursor_are_rejected(library):
    values=[row(library_id=f'BIB-SYNTH-PAGE-{i:03d}',
                 original_case_number=f'9999-{i:05d}',
                 official_source_url=OVERVIEW,
                 summary='Fiktivt robotärende.',source_text='Fiktivt robotärende.')
            for i in range(21)]
    client=index_client(library,values)
    with pytest.raises(ValueError,match='tom sökning'):
        client.search('   ')
    first=client.search('robot');cursor=client._html_state.page['next_cursor']
    with pytest.raises(ValueError,match='ändrats'):
        client.search('robot',category='el',cursor=cursor)
    with pytest.raises(ValueError,match='Ogiltig'):
        client.search('robot',cursor='not a cursor')


def test_search_tool_returns_continuation_and_each_page_uses_existing_quota(library):
    values=[row(library_id=f'BIB-SYNTH-PAGE-{i:03d}',
                 original_case_number=f'9999-{i:05d}',
                 official_source_url=OVERVIEW,
                 summary='Fiktivt robotärende.',source_text='Fiktivt robotärende.')
            for i in range(25)]
    client=index_client(library,values);events=[]
    search=load_tools(Registry(),client,License(events))['arn_search']
    first=search(query='robot')
    assert first['count']==20 and first['result_limit']==20
    assert first['total_matches']==25 and first['has_more'] is True
    second=search(query='robot',cursor=first['next_cursor'])
    assert second['count']==5 and second['has_more'] is False and second['next_cursor'] is None
    assert 'separat dataanrop' in first['continuation_cost']
    assert events==['consume','consume']


def test_relevance_ranking_prefers_summary_match_then_stable_identifier(library):
    stronger=row(library_id='BIB-SYNTH-STRONG', original_case_number='9999-90002',
                 official_source_url=OVERVIEW, summary='Robot garanti',
                 reasoning='Övrigt.', facts='Fiktivt.')
    weaker=row(library_id='BIB-SYNTH-WEAK', original_case_number='9999-90001',
               official_source_url=OVERVIEW, summary='Robot',
               reasoning='Garanti.', facts='Fiktivt.')
    client=index_client(library,[weaker,stronger])
    results=client.search('robot garanti')
    assert [r['case_number'] for r in results]==['9999-90002','9999-90001']
