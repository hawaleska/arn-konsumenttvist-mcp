import asyncio
import json
import logging
from unittest.mock import Mock

import httpx
import pytest
from starlette.applications import Starlette
from starlette.routing import Route

from conftest import load_paypal,PRIVATE,INTERNAL_URL
from test_error_contract import assert_clean


@pytest.mark.parametrize('operation',['arn_create_subscription','arn_cancel_subscription'])
def test_license_failure_at_payment_tools_is_safe(operation,caplog):
    from mcp.server.mcpserver.exceptions import ToolError
    scope=load_paypal()
    scope['license_manager'].get_active_subscription.side_effect=RuntimeError(INTERNAL_URL+' BEARER_CANARY')
    with pytest.raises(ToolError) as raised:scope[operation]()
    public=json.loads(str(raised.value))
    assert public['reference_id'] in caplog.text
    assert_clean(str(raised.value)+caplog.text)


def test_create_subscription_success_and_invalid_plan_keep_decisions(caplog):
    scope=load_paypal();license=scope['license_manager']
    license.get_active_subscription.return_value=None
    scope['paypal_access_token']=lambda:'BEARER_CANARY'
    response=Mock();response.json.return_value={'id':'synthetic-sub','links':[{'rel':'approve','href':'https://synthetic-paypal.invalid/approve'}]}
    scope['requests'].post.return_value=response
    result=scope['arn_create_subscription']('yearly')
    assert result['status']=='approval_pending' and result['amount_sek']==590
    assert result['approval_url']=='https://synthetic-paypal.invalid/approve'
    assert license.create_subscription.call_args.kwargs['status']=='APPROVAL_PENDING'
    assert scope['requests'].post.call_args.kwargs['json']['plan_id']=='synthetic-yearly'
    previous=scope['requests'].post.call_count
    error=scope['arn_create_subscription']('invalid')
    assert error['error']=='invalid_plan' and len(error['reference_id'])==32
    assert scope['requests'].post.call_count==previous
    assert_clean(caplog.text)


def test_new_user_subscription_flow_with_real_adapter_null_response(caplog):
    from unittest.mock import patch
    from test_backend_error_boundaries import manager,Response
    scope=load_paypal()
    scope['license_manager']=manager()
    scope['paypal_access_token']=lambda:'BEARER_CANARY'
    response=Mock();response.json.return_value={'id':'synthetic-sub','links':[{'rel':'approve','href':'https://synthetic-paypal.invalid/approve'}]}
    scope['requests'].post.return_value=response
    actions=[]
    def backend(request,**kwargs):
        action=json.loads(request.data)['action'];actions.append(action)
        return Response(b'null' if action=='get_active_subscription' else b'{"ok":true}')
    with patch('arn_license.urlopen',side_effect=backend):
        result=scope['arn_create_subscription']('monthly')
    assert result['status']=='approval_pending' and result['amount_sek']==59
    assert actions==['record_user_activity','get_active_subscription','ensure_user','create_subscription']
    assert_clean(caplog.text)


@pytest.mark.parametrize('status',[200,204,400,500])
def test_cancel_status_and_decision_preserved(status,caplog):
    caplog.set_level(logging.INFO)
    scope=load_paypal();license=scope['license_manager']
    license.get_active_subscription.return_value={'paypal_subscription_id':'synthetic-sub','plan':'monthly'}
    scope['paypal_access_token']=lambda:'BEARER_CANARY'
    response=Mock(status_code=status,text=INTERNAL_URL+' RAW_BODY_CANARY')
    scope['requests'].post.return_value=response
    result=scope['arn_cancel_subscription']()
    if status in (200,204):
        assert result['success'] is True
        license.mark_subscription_cancel_requested.assert_called_once_with('synthetic-sub')
        assert 'reference_id' not in result
    else:
        assert result['error']=='paypal_cancel_failed' and result['status_code']==status
        assert result['reference_id'] in caplog.text
        license.mark_subscription_cancel_requested.assert_not_called()
    assert_clean(json.dumps(result)+caplog.text)


def test_cancel_exception_correlates_reference(caplog):
    scope=load_paypal();scope['license_manager'].get_active_subscription.return_value={'paypal_subscription_id':'synthetic-sub','plan':'monthly'}
    scope['paypal_access_token']=lambda:'BEARER_CANARY'
    scope['requests'].post.side_effect=RuntimeError(INTERNAL_URL)
    result=scope['arn_cancel_subscription']()
    assert result['error']=='paypal_cancel_error' and result['reference_id'] in caplog.text
    assert_clean(json.dumps(result)+caplog.text)


@pytest.mark.parametrize('mode,expected',[('bad_json',400),('missing_headers',400),('bad_signature',401),('missing_id',400),('duplicate',200),('processing_failure',500),('success',200)])
def test_webhook_status_retry_dedup_and_safe_output(mode,expected,caplog):
    caplog.set_level(logging.INFO)
    scope=load_paypal()
    scope['verify_paypal_webhook'].return_value=mode!='bad_signature'
    scope['verify_paypal_webhook_with_api']=Mock(return_value=False)
    scope['claim_paypal_event'].return_value=mode!='duplicate'
    if mode=='processing_failure':scope['process_paypal_event'].side_effect=RuntimeError(INTERNAL_URL+' RAW_BODY_CANARY')
    event={'id':PRIVATE,'event_type':PRIVATE,'resource':{'id':PRIVATE}}
    if mode=='missing_id':event.pop('id')
    headers={key:PRIVATE for key in ('PAYPAL-AUTH-ALGO','PAYPAL-CERT-URL','PAYPAL-TRANSMISSION-ID','PAYPAL-TRANSMISSION-SIG','PAYPAL-TRANSMISSION-TIME')}
    if mode=='missing_headers':headers={}
    app=Starlette(routes=[Route('/webhook',scope['paypal_webhook'],methods=['POST'])])
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://synthetic.invalid') as client:
            return await client.post('/webhook',content=b'invalid' if mode=='bad_json' else json.dumps(event).encode(),headers=headers)
    response=asyncio.run(run())
    assert response.status_code==expected
    assert_clean(response.text+caplog.text)
    if expected>=400:
        assert response.json()['reference_id'] in caplog.text
    if mode=='processing_failure':scope['release_paypal_event'].assert_called_once_with(PRIVATE)
    if mode=='duplicate':scope['process_paypal_event'].assert_not_called()
    if mode=='success':scope['complete_paypal_event'].assert_called_once_with(PRIVATE)


def test_signature_api_logging_never_uses_headers_or_body(caplog):
    caplog.set_level(logging.INFO)
    scope=load_paypal();scope['paypal_access_token']=lambda:'BEARER_CANARY'
    response=Mock(status_code=500,text='RAW_BODY_CANARY '+INTERNAL_URL)
    scope['requests'].post.return_value=response
    assert scope['verify_paypal_webhook_with_api'](json.dumps({'id':PRIVATE,'event_type':PRIVATE}).encode(),{'PAYPAL-CERT-URL':INTERNAL_URL}) is False
    assert_clean(caplog.text)


def test_signature_fallback_failure_and_route_share_reference(caplog):
    scope=load_paypal()
    scope['verify_paypal_webhook'].return_value=False
    scope['paypal_access_token']=lambda:'BEARER_CANARY'
    scope['requests'].post.side_effect=RuntimeError(INTERNAL_URL)
    app=Starlette(routes=[Route('/webhook',scope['paypal_webhook'],methods=['POST'])])
    headers={key:PRIVATE for key in ('PAYPAL-AUTH-ALGO','PAYPAL-CERT-URL','PAYPAL-TRANSMISSION-ID','PAYPAL-TRANSMISSION-SIG','PAYPAL-TRANSMISSION-TIME')}
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://synthetic.invalid') as client:
            return await client.post('/webhook',json={'id':PRIVATE,'event_type':PRIVATE},headers=headers)
    response=asyncio.run(run())
    assert response.status_code==401
    records=[json.loads(r.message) for r in caplog.records if r.name=='arn.errors' and 'reference_id' in r.message]
    assert records and {r['reference_id'] for r in records}=={response.json()['reference_id']}
    assert_clean(response.text+caplog.text)
