"""Synthetic HTML summaries through unchanged production tool/payment bodies."""
import copy
import json
import hashlib
import pytest
from arn_library_client import SummaryLibraryClient, LibraryUnavailable, content_sha256
from conftest import load_tools, Registry, License
from library_lifecycle import revoke
from test_reviewed_library import library, no_network, record, approve, ARGS, existing_control


def row(**changes):
    value=record(content_type='html_summary',source_text='En fiktiv robot hade fel och avhjälpande uteblev.',
                 outcome='okant',companies=[],facts='',reasoning='',disposition='',date='')
    value.update(changes)
    return value


def approval(value):
    return {**approve(value),'publication_review':{'status':'approved','reference':'REVIEW-SYNTHETIC-001',
             'sensitive_context':'none_identified','basis_reference':'','full_text_review':'not_full_text'}}


def build(library, rows, approvals=None):
    client=library(rows,approvals if approvals is not None else [approval(r) for r in rows])
    return SummaryLibraryClient(client.library_path,client.approvals_path,client.approvals_sha256,
                                allow_synthetic=True,**existing_control(client))


@pytest.mark.parametrize('tool',sorted(ARGS))
def test_six_real_production_tools_accept_summary_without_live_access(library,tool):
    client=build(library,[row()]); events=[]
    result=load_tools(Registry(),client,License(events))[tool](**ARGS[tool])
    rows=[result['results']] if tool=='arn_get_decision' else result.get('decisions',result.get('results'))
    if tool in ('arn_search_company','arn_search_company_and_read'):
        assert rows==[]  # No invented company for an unknown company field.
    else:
        assert len(rows)==1
        if tool in ('arn_get_decision','arn_search_and_read'):
            assert 'inte hela ARN-beslutet' in rows[0]['text']
    assert events==['consume']


def test_unknown_fields_original_reference_and_hash_remain_truthful(library):
    value=row(original_case_number='9999-90001',official_source_url='https://www.arn.se/om-arn/vagledande-beslut/')
    before=content_sha256(value);client=build(library,[value])
    result=client.get_decision('9999-90001')
    assert result['case_number']=='9999-90001' and result['date']=='okänt'
    assert content_sha256(value)==before and client.search('robot')
    assert client.search('robot',outcome='bifall')==[]
    assert client.similar_cases('anonymiserad')['results']==[]


@pytest.mark.parametrize('change',[{'status':'pending'},{'legal_review':'pending'},
                                 {'content_sha256':'0'*64},{'publication_review':None},
                                 {'publication_review':{'status':'approved'}}])
def test_unapproved_summary_never_exposed(library,change):
    value=row();a=approval(value);a.update(change)
    client=build(library,[value],[a]);assert client.search('')==[]
    with pytest.raises(LibraryUnavailable):client.get_decision(value['library_id'])


def test_legacy_record_and_missing_summary_review_are_blocked(library):
    assert build(library,[record()],[approve(record())]).search('')==[]
    value=row();assert build(library,[value],[approve(value)]).search('')==[]
    bad=row(full_text='Not part of 1.0.4');assert build(library,[bad]).search('')==[]


def test_revoke_survives_older_summary_content_restore(library):
    value=row();client=build(library,[value]);saved=client.library_path.read_bytes()
    assert client.search('robot')
    revoke(client.revocations,value['library_id'],'CASE-000000000000000000000001')
    client.library_path.write_bytes(saved)
    assert client.search('')==[] and client.similar_cases('robot')['results']==[]


def test_modified_summary_fails_original_content_hash(library):
    value=row();client=build(library,[value]);data=json.loads(client.library_path.read_bytes())
    data['records'][0]['source_text']+=' Manipulated synthetic text.'
    client.library_path.write_text(json.dumps(data),encoding='utf-8')
    assert client.search('')==[]


@pytest.mark.parametrize('reference',['BIB-TEST-1',' BIB-TEST-1 ','\nBIB-TEST-1\t'])
def test_read_preserves_legacy_outer_whitespace_handling(library,reference):
    client=build(library,[row()])
    assert client.get_decision(reference)['case_number']=='BIB-TEST-1'


def test_missing_reference_diagnostics_are_neutral_and_keep_error_contract(library,caplog):
    from mcp.server.mcpserver.exceptions import ToolError
    client=build(library,[row()]);events=[]
    with pytest.raises(ToolError) as failure:
        load_tools(Registry(),client,License(events))['arn_get_decision'](case_number='PRIVATE-CANARY@example.invalid')
    public=json.loads(str(failure.value))
    assert set(public)=={'error','message','reference_id'} and public['error']=='result_unavailable'
    diagnostics=[json.loads(r.getMessage()) for r in caplog.records if 'diagnostic_stage' in r.getMessage()]
    assert diagnostics and diagnostics[-1]['reference_id']==public['reference_id']
    assert diagnostics[-1]['diagnostic_stage']=='reference_not_found'
    assert diagnostics[-1]['exception_class']=='LibraryUnavailable'
    assert diagnostics[-1]['reference_format_known'] is False
    assert 'PRIVATE-CANARY' not in str(failure.value) and 'PRIVATE-CANARY' not in caplog.text
    assert events==['consume']


def test_before_library_error_is_distinguished_without_logging_exception(library,caplog):
    from mcp.server.mcpserver.exceptions import ToolError
    client=build(library,[row()]);tools=load_tools(Registry(),client,License([]))
    def broken():raise ValueError('PRIVATE-AUTH-CANARY')
    tools['get_authenticated_user_id']=broken
    with pytest.raises(ToolError):tools['arn_get_decision'](case_number='BIB-TEST-1')
    diagnostics=[json.loads(r.getMessage()) for r in caplog.records if 'diagnostic_stage' in r.getMessage()]
    assert diagnostics[-1]['diagnostic_stage']=='tool_execution'
    assert diagnostics[-1]['exception_class']=='ValueError'
    assert 'PRIVATE-AUTH-CANARY' not in caplog.text


@pytest.mark.parametrize('reference',[None,'', '   '])
def test_empty_or_invalid_reference_cannot_select_missing_original_alias(library,reference):
    client=build(library,[row()])
    with pytest.raises(LibraryUnavailable):client.get_decision(reference)
