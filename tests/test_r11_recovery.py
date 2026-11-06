"""R11 review regressions. Synthetic databases, provider responses and processes."""
import ast
import asyncio
from contextlib import closing
import copy
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from unittest.mock import Mock

import pytest
from starlette.requests import Request

from conftest import ROOT, load_paypal
from arn_paypal_store import payment_lock, PaymentBusy, payment_connection, creation_intent
from test_release_paypal import setup


def webhook_scope(tmp_path):
    scope = load_paypal()
    scope.update(LICENSE_DB=tmp_path/'synthetic.db', sqlite3=sqlite3,
                 payment_connection=payment_connection)
    names = {'init_paypal_webhook_store', 'claim_paypal_event',
             'complete_paypal_event', 'release_paypal_event'}
    nodes = [n for n in ast.parse((ROOT/'arn_mcp.py').read_text(encoding='utf-8')).body
             if isinstance(n, ast.FunctionDef) and n.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'actual-webhook-store', 'exec'), scope)
    scope['init_paypal_webhook_store']()
    return scope


def status(scope):
    with closing(sqlite3.connect(scope['LICENSE_DB'])) as conn:
        return conn.execute('SELECT status FROM paypal_webhook_events WHERE event_id=?', ('EV-SYNTHETIC',)).fetchone()[0]


def deliver(scope):
    with payment_lock(scope['LICENSE_DB']):
        return scope['handle_paypal_delivery']({'id':'EV-SYNTHETIC'}, 'EV-SYNTHETIC', 'TYPE-SYNTHETIC')


@pytest.mark.parametrize('phase', ['before_backend', 'after_backend'])
def test_real_process_death_recovers_without_double_backend_effect(tmp_path, phase):
    scope = webhook_scope(tmp_path)
    database = scope['LICENSE_DB']
    with payment_connection(database) as conn:
        conn.execute('CREATE TABLE synthetic_effects(event_id TEXT PRIMARY KEY, value TEXT)')
    code = r'''
import ast, os, sys
from pathlib import Path
from datetime import datetime, timezone
from arn_paypal_store import payment_lock, payment_connection
database, source, phase = sys.argv[1:]
scope=dict(LICENSE_DB=database, datetime=datetime, timezone=timezone, payment_connection=payment_connection)
names={'claim_paypal_event'}
nodes=[n for n in ast.parse(Path(source).read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name in names]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'actual-claim','exec'),scope)
with payment_lock(database):
    assert scope['claim_paypal_event']('EV-SYNTHETIC','TYPE-SYNTHETIC')
    if phase=='after_backend':
        with payment_connection(database) as conn:
            conn.execute("INSERT OR REPLACE INTO synthetic_effects VALUES ('EV-SYNTHETIC','done')")
    os._exit(23)
'''
    result = subprocess.run([sys.executable, '-B', '-c', code, str(database), str(ROOT/'arn_mcp.py'), phase],
                            cwd=ROOT, capture_output=True, text=True, timeout=15)
    assert result.returncode == 23, result.stderr
    assert status(scope) == 'processing'
    def idempotent_backend(event):
        with payment_connection(database) as conn:
            conn.execute("INSERT INTO synthetic_effects VALUES (?, 'done') ON CONFLICT(event_id) DO UPDATE SET value='done'", (event['id'],))
    scope['process_paypal_event'] = Mock(side_effect=idempotent_backend)
    assert deliver(scope).status_code == 200
    assert status(scope) == 'completed'
    assert deliver(scope).body == b'{"status":"already_processed"}'
    scope['process_paypal_event'].assert_called_once()
    with closing(sqlite3.connect(database)) as conn:
        assert conn.execute('SELECT count(*) FROM synthetic_effects').fetchone()[0] == 1


def test_failed_delivery_is_retained_and_retried(tmp_path):
    scope = webhook_scope(tmp_path)
    scope['process_paypal_event'].side_effect = RuntimeError('SYNTHETIC-PRIVATE')
    assert deliver(scope).status_code == 500
    assert status(scope) == 'failed'
    scope['process_paypal_event'].side_effect = None
    assert deliver(scope).status_code == 200
    assert status(scope) == 'completed'


@pytest.mark.parametrize('legacy_status', ['processed', 'completed'])
def test_historical_completed_event_remains_deduplicated(tmp_path, legacy_status):
    scope = webhook_scope(tmp_path)
    with payment_connection(scope['LICENSE_DB']) as conn:
        conn.execute('INSERT INTO paypal_webhook_events VALUES (?, ?, ?, ?, ?)',
                     ('EV-SYNTHETIC', 'TYPE-SYNTHETIC', 'synthetic-time', None, legacy_status))
    assert deliver(scope).body == b'{"status":"already_processed"}'
    scope['process_paypal_event'].assert_not_called()
    assert status(scope) == legacy_status


def test_parallel_unfinished_delivery_gets_retryable_http_not_200(tmp_path):
    scope = webhook_scope(tmp_path)
    headers=[(name.lower().encode(), b'synthetic') for name in
             ('PAYPAL-AUTH-ALGO','PAYPAL-CERT-URL','PAYPAL-TRANSMISSION-ID','PAYPAL-TRANSMISSION-SIG','PAYPAL-TRANSMISSION-TIME')]
    async def receive():
        return {'type':'http.request','body':b'{"id":"EV-SYNTHETIC"}','more_body':False}
    with payment_lock(scope['LICENSE_DB']):
        assert scope['claim_paypal_event']('EV-SYNTHETIC', 'TYPE-SYNTHETIC')
        response=asyncio.run(scope['paypal_webhook'](Request({'type':'http','method':'POST','headers':headers}, receive)))
        assert response.status_code == 503
        assert b'already_processed' not in response.body
    scope['process_paypal_event'].assert_not_called()
    assert status(scope) == 'processing'
    assert deliver(scope).status_code == 200


def creation_scope():
    scope=load_paypal()
    scope['license_manager'].get_active_subscription.return_value=None
    scope['paypal_access_token']=lambda:'synthetic-not-a-real-token'
    response=Mock()
    response.json.return_value={'id':'I-SYNTHETIC', 'links':[{'rel':'approve','href':'https://synthetic.invalid/approve'}]}
    scope['requests'].post.return_value=response
    return scope


def test_user_registration_failure_precedes_any_external_creation():
    scope=creation_scope()
    scope['license_manager'].ensure_user.side_effect=RuntimeError('synthetic-down')
    with pytest.raises(Exception):scope['arn_create_subscription']()
    scope['requests'].post.assert_not_called()


def test_backend_failure_after_external_creation_is_recoverable_without_second_post():
    scope=creation_scope()
    scope['license_manager'].create_subscription.side_effect=RuntimeError('synthetic-down')
    with pytest.raises(Exception):scope['arn_create_subscription']()
    intent=creation_intent(scope['LICENSE_DB'],'synthetic-user','monthly')
    assert intent['state']=='provider_created' and intent['subscription_id']=='I-SYNTHETIC'
    assert scope['requests'].post.call_args.kwargs['headers']['PayPal-Request-Id']==intent['request_id']
    scope['license_manager'].create_subscription.side_effect=None
    assert scope['arn_create_subscription']()['paypal_subscription_id']=='I-SYNTHETIC'
    scope['requests'].post.assert_called_once()


def test_uncertain_external_creation_never_blindly_repeats():
    scope=creation_scope()
    scope['requests'].post.side_effect=TimeoutError('synthetic-uncertain')
    for _ in range(2):
        with pytest.raises(Exception):scope['arn_create_subscription']()
    scope['requests'].post.assert_called_once()
    intent=creation_intent(scope['LICENSE_DB'],'synthetic-user','monthly')
    assert intent['state']=='attempted' and intent['subscription_id'] is None


def test_confirmed_terminal_subscription_allows_new_request_and_keeps_history():
    scope=creation_scope()
    scope['arn_create_subscription']()
    old=creation_intent(scope['LICENSE_DB'],'synthetic-user','monthly')
    scope['license_manager'].get_subscription_by_paypal_id.return_value={'status':'CANCELLED'}
    scope['paypal_subscription_details']=lambda value:{'id':value,'status':'CANCELLED','custom_id':'synthetic-user'}
    response=Mock()
    response.json.return_value={'id':'I-SECOND-SYNTHETIC','links':[]}
    scope['requests'].post.return_value=response
    assert scope['arn_create_subscription']('yearly')['paypal_subscription_id']=='I-SECOND-SYNTHETIC'
    current=creation_intent(scope['LICENSE_DB'],'synthetic-user','yearly')
    assert current['request_id']!=old['request_id']
    with closing(sqlite3.connect(scope['LICENSE_DB'])) as conn:
        assert conn.execute('SELECT count(*) FROM paypal_creation_intents').fetchone()[0]==2
        assert conn.execute('SELECT state FROM paypal_creation_intents WHERE request_id=?',(old['request_id'],)).fetchone()[0]=='retired'


@pytest.mark.parametrize('plan,start,end,paid,now', [
    ('monthly','2026-01-31T12:00:00Z','2026-03-31T12:00:00Z','2026-02-28T12:00:00Z','2026-03-01T12:00:00Z'),
    ('yearly','2024-02-29T12:00:00Z','2025-02-28T12:00:00Z','2024-02-29T12:00:00Z','2024-11-01T12:00:00Z'),
])
def test_calendar_boundaries_preserve_original_anchor(plan,start,end,paid,now):
    scope,data=setup()
    class Clock(datetime):
        @classmethod
        def now(cls,tz=None):return datetime.fromisoformat(now.replace('Z','+00:00'))
    scope['datetime']=Clock
    data.update(plan_id='synthetic-'+plan,start_time=start)
    data['billing_info']['next_billing_time']=end
    data['billing_info']['last_payment']={'time':paid,'amount':{'currency_code':'SEK','value':'590' if plan=='yearly' else '59'}}
    if plan=='monthly':
        scope['paid_period'](scope['LICENSE_DB'],data['id'],datetime.fromisoformat(paid.replace('Z','+00:00')).isoformat())
    assert scope['record_verified_subscription'](data['id'],data)=='verified'
    expected=datetime.fromisoformat(end.replace('Z','+00:00')).isoformat()
    assert scope['license_manager'].create_subscription.call_args.kwargs['expires_at']==expected


def test_missing_previous_cycle_proof_never_treats_catchup_payment_as_current():
    scope,data=setup()
    start=datetime.fromisoformat(data['start_time'])
    data['start_time']=start.replace(year=start.year-1).isoformat()
    assert scope['record_verified_subscription'](data['id'],data)=='pending'
    scope['license_manager'].activate_paid.assert_not_called()


@pytest.mark.parametrize('plan', ['monthly','yearly'])
def test_provider_billing_clock_need_not_equal_initial_start_clock(plan):
    scope,data=setup()
    class Clock(datetime):
        @classmethod
        def now(cls,tz=None):return datetime(2026,11,6,12,tzinfo=timezone.utc)
    scope['datetime']=Clock
    data.update(plan_id='synthetic-'+plan,start_time='2026-11-06T01:23:45Z')
    end='2026-12-06T10:00:00Z' if plan=='monthly' else '2027-11-06T10:00:00Z'
    data['billing_info']['next_billing_time']=end
    data['billing_info']['last_payment']={'time':'2026-11-06T02:00:00Z',
        'amount':{'currency_code':'SEK','value':'59' if plan=='monthly' else '590'}}
    assert scope['record_verified_subscription'](data['id'],data)=='verified'
    assert scope['license_manager'].create_subscription.call_args.kwargs['expires_at']==end.replace('Z','+00:00')


def test_provider_billing_date_mismatch_still_denies_access():
    scope,data=setup()
    end=datetime.fromisoformat(data['billing_info']['next_billing_time'])+timedelta(days=1)
    data['billing_info']['next_billing_time']=end.isoformat()
    assert scope['record_verified_subscription'](data['id'],data)=='pending'
    scope['license_manager'].activate_paid.assert_not_called()


@pytest.mark.parametrize('next_link', [False,True])
def test_optional_transaction_paging_counter_and_explicit_next_link(next_link):
    scope,data=setup()
    original=scope['requests'].get.side_effect
    def provider(url,**kwargs):
        response=original(url,**kwargs)
        if url.endswith('/transactions'):
            value=response.json();value.pop('total_pages')
            if next_link:value['links']=[{'rel':'next','href':'https://synthetic.invalid/next'}]
        return response
    scope['requests'].get.side_effect=provider
    assert scope['record_verified_subscription'](data['id'],data)==('pending' if next_link else 'verified')
    assert scope['license_manager'].activate_paid.call_count==(0 if next_link else 1)


def test_refund_invalidates_cached_current_payment_evidence():
    scope,data=setup()
    scope['paid_period'](scope['LICENSE_DB'],data['id'],data['billing_info']['next_billing_time'])
    provider=scope['requests'].get.side_effect
    def refunded(url,**kwargs):
        response=provider(url,**kwargs)
        if url.endswith('/transactions'):response.json()['transactions'][0]['status']='REFUNDED'
        return response
    scope['requests'].get.side_effect=refunded
    assert scope['record_verified_subscription'](data['id'],data)=='pending'
    assert scope['paid_period'](scope['LICENSE_DB'],data['id']) is None
    scope['license_manager'].activate_paid.assert_not_called()


@pytest.mark.parametrize('mutation', [
    'no_payment','old_payment','wrong_amount','wrong_currency','future_payment',
    'failure','outstanding','no_balance','override','quantity','unaligned_end'])
def test_active_plus_future_date_never_substitutes_for_payment(mutation):
    scope,data=setup()
    billing=data['billing_info']
    if mutation=='no_payment':billing.pop('last_payment')
    if mutation=='old_payment':billing['last_payment']['time']='2000-01-01T00:00:00Z'
    if mutation=='wrong_amount':billing['last_payment']['amount']['value']='1'
    if mutation=='wrong_currency':billing['last_payment']['amount']['currency_code']='USD'
    if mutation=='future_payment':billing['last_payment']['time']='2099-01-01T00:00:00Z'
    if mutation=='failure':billing['failed_payments_count']=1
    if mutation=='outstanding':billing['outstanding_balance']['value']='59'
    if mutation=='no_balance':billing.pop('outstanding_balance')
    if mutation=='override':data['plan_overridden']=True
    if mutation=='quantity':data['quantity']='2'
    if mutation=='unaligned_end':billing['next_billing_time']='2099-01-01T00:00:00Z'
    assert scope['record_verified_subscription'](data['id'],data)=='pending'
    assert scope['license_manager'].create_subscription.call_args.kwargs['expires_at'] is None
    scope['license_manager'].activate_paid.assert_not_called()


@pytest.mark.parametrize('mode', ['PENDING','REFUNDED','PARTIALLY_REFUNDED','DENIED','wrong_amount','wrong_time','duplicate','pages','trial','network'])
def test_independent_provider_payment_or_plan_evidence_required(mode):
    scope,data=setup()
    original=scope['requests'].get.side_effect
    def provider(url,**kwargs):
        response=original(url,**kwargs)
        body=response.json()
        if mode=='network' and url.endswith('/transactions'):
            raise TimeoutError('synthetic-down')
        if '/plans/' in url and mode=='trial':body['billing_cycles'][0]['tenure_type']='TRIAL'
        if url.endswith('/transactions'):
            transaction=body['transactions'][0]
            if mode in {'PENDING','REFUNDED','PARTIALLY_REFUNDED','DENIED'}:transaction['status']=mode
            if mode=='wrong_amount':transaction['amount_with_breakdown']['gross_amount']['value']='1'
            if mode=='wrong_time':transaction['time']='2000-01-01T00:00:00Z'
            if mode=='duplicate':body['transactions'].append(copy.deepcopy(transaction))
            if mode=='pages':body['total_pages']=2
        return response
    scope['requests'].get.side_effect=provider
    if mode=='network':
        with pytest.raises(TimeoutError):scope['record_verified_subscription'](data['id'],data)
        scope['license_manager'].create_subscription.assert_not_called()
    else:
        assert scope['record_verified_subscription'](data['id'],data)=='pending'
        assert scope['license_manager'].create_subscription.call_args.kwargs['expires_at'] is None
    scope['license_manager'].activate_paid.assert_not_called()


def test_failure_does_not_extend_previously_verified_paid_period():
    scope,data=setup()
    previous=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()
    scope['paid_period'](scope['LICENSE_DB'],data['id'],previous)
    data['billing_info']['failed_payments_count']=1
    assert scope['record_verified_subscription'](data['id'],data)=='verified'
    assert scope['license_manager'].create_subscription.call_args.kwargs['expires_at']==previous


def test_legacy_expiry_is_not_treated_as_payment_proof():
    scope,data=setup()
    data.update(status='CANCELLED',billing_info={})
    scope['license_manager'].get_subscription_by_paypal_id.return_value={
        'user_id':'user-A','paypal_subscription_id':data['id'],'expires_at':'2099-01-01T00:00:00Z'}
    assert scope['record_verified_subscription'](data['id'],data)=='inactive'
    assert scope['license_manager'].create_subscription.call_args.kwargs['expires_at'] is None
