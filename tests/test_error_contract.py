import ast
import json
import logging
import re
from pathlib import Path

import pytest

from arn_errors import failure,public_error,safe_event,safe_exception,tool_errors
from arn_public_responses import public_decision
from conftest import PRIVATE,INTERNAL_URL,ROOT


def assert_clean(text):
    for bad in (PRIVATE,INTERNAL_URL,'BEARER_CANARY','RAW_BODY_CANARY','private@example.invalid'):
        assert bad not in text


def test_reference_same_in_public_and_log_and_no_raw_error(caplog):
    caplog.set_level(logging.INFO)
    exc=RuntimeError(INTERNAL_URL+' BEARER_CANARY RAW_BODY_CANARY private@example.invalid\r\nInjected')
    err=failure('decision_unavailable','arn_get_decision',exc)
    public=public_decision({'case_number':'synthetic','error':err,'file_id':PRIVATE})
    assert re.fullmatch('[0-9a-f]{32}',public['reference_id'])
    assert public['reference_id']==err.reference_id
    records=[json.loads(r.message) for r in caplog.records if r.name=='arn.errors']
    assert len(records)==1 and records[0]['reference_id']==public['reference_id']
    assert_clean(json.dumps(public)+caplog.text)
    failure('decision_unavailable','arn_get_decision',exc)
    assert len(caplog.records)==1


def test_upstream_cannot_supply_reference_or_error_message(caplog):
    result=public_decision({'error':{'error':'decision_unavailable','reference_id':PRIVATE,'message':INTERNAL_URL},'reference_id':PRIVATE})
    assert len(result['reference_id'])==32 and result['reference_id']!=PRIVATE
    assert_clean(json.dumps(result)+caplog.text)


def test_forged_internal_marker_is_revalidated(caplog):
    from arn_errors import _Failure
    result=public_error(_Failure('decision_unavailable',PRIVATE),'decision_unavailable','public_response')
    assert re.fullmatch('[0-9a-f]{32}',result['reference_id'])
    assert_clean(json.dumps(result)+caplog.text)


def test_reference_context_is_task_local_and_resets():
    import asyncio
    from arn_errors import error_context
    async def request():
        with error_context():
            first=failure('backend_unavailable','license_request')
            await asyncio.sleep(0)
            second=failure('signature_invalid','paypal_webhook')
            assert first.reference_id==second.reference_id
            return first.reference_id
    async def run():return await asyncio.gather(request(),request())
    ids=asyncio.run(run())
    assert ids[0]!=ids[1]
    assert failure('result_unavailable','arn_search').reference_id not in ids


def test_error_ids_are_distinct_and_no_sensitive_log_classification(caplog):
    caplog.set_level(logging.INFO)
    first=failure('unknown_sensitive_code','injected\r\n'+PRIVATE)
    second=failure('result_unavailable','arn_search')
    assert first.reference_id!=second.reference_id
    safe_event(INTERNAL_URL,'BEARER_CANARY',status=PRIVATE)
    assert_clean(caplog.text)


@pytest.mark.parametrize('category',[ValueError,PermissionError,RuntimeError])
def test_safe_exception_preserves_category_without_original_text(category,caplog):
    original=category(INTERNAL_URL)
    safe=safe_exception(category,'backend_unavailable','license_request',original)
    assert isinstance(safe,category)
    assert safe._arn_safe_failure.reference_id in caplog.text
    assert_clean(str(safe)+caplog.text)


def test_successful_paypal_dictionary_is_identical():
    success={'status':'approval_pending','approval_url':'https://synthetic-paypal.invalid/approve','paypal_subscription_id':'synthetic-subscription'}
    @tool_errors('arn_create_subscription')
    def function():return success
    assert function() is success


def test_domain_error_extra_fields_are_explicit_not_backend_bags():
    @tool_errors('arn_create_subscription')
    def function():
        return {'error':'already_subscribed','message':INTERNAL_URL,'subscription_id':'synthetic-sub',
                'plan':'monthly','unknown':{'raw':PRIVATE},'reference_id':PRIVATE}
    result=function()
    assert set(result)=={'error','message','reference_id','subscription_id','plan'}
    assert result['subscription_id']=='synthetic-sub'
    assert_clean(json.dumps(result))


def test_no_raw_error_sinks_left_in_five_candidates():
    for name in ('arn_mcp.py','arn_client.py','arn_license.py','arn_public_responses.py','arn_errors.py'):
        tree=ast.parse((ROOT/name).read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):
                assert node.func.id!='print'
                if node.func.id in ('str','repr'):
                    assert not any(isinstance(a,ast.Name) and a.id in ('exc','error') for a in node.args)
