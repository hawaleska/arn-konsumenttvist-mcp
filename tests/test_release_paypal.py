"""R10/R11 exact candidate functions; only synthetic HTTP responses."""
import ast
import asyncio
import copy
import os
from unittest.mock import Mock
import pytest
from starlette.requests import Request
from conftest import ROOT, load_paypal

ENV={'PAYPAL_ENV':'sandbox','PAYPAL_CLIENT_ID':'synthetic-client',
     'PAYPAL_CLIENT_SECRET':'synthetic-secret','PAYPAL_WEBHOOK_ID':'synthetic-hook',
     'PAYPAL_MONTHLY_PLAN_ID':'synthetic-monthly','PAYPAL_YEARLY_PLAN_ID':'synthetic-yearly'}

def config(env):
    source=(ROOT/'arn_mcp.py').read_text(encoding='utf-8')
    start=source.index('def required_env(');end=source.index('PAYPAL_MONTHLY_AMOUNT',start)
    scope={'os':Mock(environ=env)};scope['os'].getenv=lambda name,default=None:env.get(name,default)
    exec(source[start:end],scope)
    return scope

@pytest.mark.parametrize('missing',list(ENV))
def test_required_paypal_settings_fail_before_network(missing):
    env=dict(ENV);env.pop(missing)
    with pytest.raises(RuntimeError):config(env)

@pytest.mark.parametrize('invalid',['production','sandboox','', 'https://invalid.example'])
def test_unknown_environment_rejected(invalid):
    with pytest.raises(RuntimeError):config(dict(ENV,PAYPAL_ENV=invalid))

@pytest.mark.parametrize('env,host',[('live','https://api-m.paypal.com'),('sandbox','https://api-m.sandbox.paypal.com')])
def test_only_expected_paypal_host(env,host):
    assert config(dict(ENV,PAYPAL_ENV=env))['PAYPAL_API_BASE']==host

def test_plans_must_be_distinct():
    with pytest.raises(RuntimeError):config(dict(ENV,PAYPAL_YEARLY_PLAN_ID='synthetic-monthly'))

def setup():
    scope=load_paypal();scope['license_manager'].get_subscription_by_paypal_id.return_value=None
    scope['paypal_access_token']=lambda:'synthetic-token'
    details={'id':'I-SYNTHETIC','plan_id':'synthetic-monthly','custom_id':'user-A','status':'ACTIVE',
             'billing_info':{'next_billing_time':'2099-12-31T00:00:00Z'}}
    response=Mock();response.json.return_value=details
    scope['requests'].get.return_value=response
    return scope,details

@pytest.mark.parametrize('status,expected',[('ACTIVE','verified'),('APPROVED','pending'),('APPROVAL_PENDING','pending'),
    ('CREATED','pending'),('SUSPENDED','inactive'),('CANCELLED','inactive'),('EXPIRED','inactive')])
def test_activation_requires_active_verified_plan(status,expected):
    scope,data=setup();data['status']=status
    result=scope['record_verified_subscription'](data['id'],data)
    assert result==expected
    assert scope['license_manager'].activate_paid.call_count==(status=='ACTIVE')
    stored=scope['license_manager'].create_subscription.call_args.kwargs
    assert stored['status']==status and stored['expires_at']=='2099-12-31T00:00:00Z'

@pytest.mark.parametrize('change',[{'id':'I-OTHER'},{'plan_id':'foreign-plan'},{'status':'UNVERIFIED'},
    {'custom_id':None},{'billing_info':{'next_billing_time':'not-a-date'}},
    {'billing_info':{}},{'billing_info':{'next_billing_time':'2000-01-01T00:00:00Z'}},
    {'billing_info':{'next_billing_time':'2099-01-01'}}])
def test_unverified_details_never_write_or_activate(change):
    scope,data=setup();data.update(change)
    with pytest.raises(ValueError):scope['record_verified_subscription']('I-SYNTHETIC',data)
    scope['license_manager'].create_subscription.assert_not_called()
    scope['license_manager'].activate_paid.assert_not_called()

def test_different_user_binding_is_rejected():
    scope,data=setup()
    scope['license_manager'].get_subscription_by_paypal_id.return_value={'user_id':'user-B','paypal_subscription_id':data['id']}
    with pytest.raises(ValueError):scope['record_verified_subscription'](data['id'],data)
    scope['license_manager'].create_subscription.assert_not_called()

def test_cancellation_preserves_previously_verified_period():
    scope,data=setup();data.update(status='CANCELLED',billing_info={})
    scope['license_manager'].get_subscription_by_paypal_id.return_value={
        'user_id':'user-A','paypal_subscription_id':data['id'],'expires_at':'2099-01-01T00:00:00Z'}
    scope['record_verified_subscription'](data['id'],data)
    assert scope['license_manager'].create_subscription.call_args.kwargs['expires_at']=='2099-01-01T00:00:00Z'
    scope['license_manager'].activate_paid.assert_not_called()

@pytest.mark.parametrize('plan,amount',[('monthly',59),('yearly',590)])
def test_both_allowed_plans_store_expected_price_and_renewed_boundary(plan,amount):
    scope,data=setup();data['plan_id']='synthetic-'+plan
    scope['license_manager'].get_subscription_by_paypal_id.return_value={
        'user_id':'user-A','paypal_subscription_id':data['id'],'expires_at':'2098-01-01T00:00:00Z'}
    assert scope['record_verified_subscription'](data['id'],data)=='verified'
    stored=scope['license_manager'].create_subscription.call_args.kwargs
    assert stored['plan']==plan and stored['amount_sek']==amount
    assert stored['expires_at']=='2099-12-31T00:00:00Z'

@pytest.mark.parametrize('mode,code',[('missing',400),('network',400),('pending',202),('active',200),('expired',409),('foreign',400)])
def test_success_page_never_claims_unverified_activation(mode,code,caplog):
    scope,data=setup()
    if mode=='network':scope['requests'].get.side_effect=RuntimeError('SYNTHETIC_SECRET_CANARY')
    if mode=='pending':data['status']='APPROVED'
    if mode=='expired':data['status']='EXPIRED'
    if mode=='foreign':data['plan_id']='foreign-plan'
    query=b'' if mode=='missing' else b'subscription_id=I-SYNTHETIC'
    response=asyncio.run(scope['paypal_success'](Request({'type':'http','method':'GET','path':'/paypal/success','query_string':query,'headers':[]})))
    assert response.status_code==code and response.headers['cache-control']=='no-store'
    assert 'I-SYNTHETIC' not in response.body.decode()+caplog.text
    assert 'SYNTHETIC_SECRET_CANARY' not in response.body.decode()+caplog.text
    assert scope['license_manager'].activate_paid.call_count==(mode=='active')

def test_delayed_active_webhook_uses_current_expired_provider_status():
    scope,data=setup();data['status']='EXPIRED'
    tree=ast.parse((ROOT/'arn_mcp.py').read_text(encoding='utf-8'))
    names={'process_paypal_event','get_subscription_id_from_resource'}
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'real-event-processing','exec'),scope)
    scope['process_paypal_event']({'id':'event-synthetic','event_type':'BILLING.SUBSCRIPTION.ACTIVATED','resource':{'id':data['id'],'status':'ACTIVE'}})
    scope['requests'].get.assert_called_once()
    scope['license_manager'].activate_paid.assert_not_called()
    assert scope['license_manager'].create_subscription.call_args.kwargs['status']=='EXPIRED'
