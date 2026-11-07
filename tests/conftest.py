import ast
import copy
from pathlib import Path
import sys
import types
import importlib.util
import json
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from arn_public_responses import public_response, TOOLS
from arn_errors import failure, safe_event, tool_errors, route_errors, http_error

if importlib.util.find_spec('mcp') is None:
    exceptions=types.ModuleType('mcp.server.mcpserver.exceptions')
    class SyntheticToolError(Exception):
        pass
    exceptions.ToolError=SyntheticToolError
    sys.modules['mcp.server.mcpserver.exceptions']=exceptions

PRIVATE = 'PRIVATE_SESSION_CANARY'
INTERNAL_URL = 'https://adokweb.arn.se/digiforms/sessionInitializer?xsessiontag='+PRIVATE+'&fileId=1'


def decision():
    return {'case_number':'2026-00001','date':'2026-01-01','category':'Test',
            'summary':'Syntetiskt referat','text':'Syntetisk beslutstext','pages':2,
            'file_id':PRIVATE,'xsessiontag':PRIVATE,'pdf_url':INTERNAL_URL,
            'unknown':{'nested':PRIVATE},'source':INTERNAL_URL}


def license_status(allowed=True):
    return {'allowed':allowed,'paid':False,'remaining':9,'searches_used':1,'free_searches':10,
            'user_id':PRIVATE,'backend_url':INTERNAL_URL,'unknown':{'token':PRIVATE}}


class Client:
    def __init__(self, events):
        self.events=events
        self.rows=[decision()]
        self.failure=False
        self.search_failure=False

    def search(self, **kwargs):
        self.events.append('search')
        if self.search_failure:
            raise RuntimeError(INTERNAL_URL)
        return self.rows

    def get_decision(self, **kwargs):
        self.events.append(('get_decision',copy.deepcopy(kwargs)))
        if self.failure:
            raise RuntimeError(INTERNAL_URL)
        return decision()

    def similar_cases(self, **kwargs):
        self.events.append('similar_cases')
        return {'problem':kwargs['problem'],'concepts':['test'], 'search_terms':['test'],
                'count':1,'results':[{**decision(),'score':12.5,'matched_queries':['test']}],
                'common_cases':[{'case_number':'2026-00002','category':'Test','area':'Test',
                                 'description':'Syntetiskt vanligt fall','source':INTERNAL_URL,
                                 'file_id':PRIVATE,'unexpected':{'secret':PRIVATE}}],
                'unexpected':PRIVATE}


class License:
    def __init__(self,events):self.events=events;self.allowed=True;self.activity=[]
    def record_user_activity(self,user):self.activity.append(user)
    def check(self,user):self.events.append('check');return license_status(self.allowed)
    def consume(self,user):self.events.append('consume');return license_status(self.allowed)


class Registry:
    def tool(self,**kwargs):return lambda function:function


def load_tools(server, client, license):
    """Compile exact six function definitions; never execute .env/payment startup."""
    tree=ast.parse((ROOT/'arn_mcp.py').read_text(encoding='utf-8'))
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in TOOLS]
    assert len(functions)==6
    annotations=types.SimpleNamespace
    try:
        from mcp.types import ToolAnnotations
        annotations=ToolAnnotations
    except ModuleNotFoundError:
        pass
    scope={'__name__':'synthetic_arn_tools','server':server,'client':client,'license_manager':license,
           'get_authenticated_user_id':lambda:'synthetic-user','public_response':public_response,
           'ToolAnnotations':annotations,'failure':failure}
    exec(compile(ast.Module(body=functions,type_ignores=[]),'arn_mcp_six_tools.py','exec'),scope)
    return scope


@pytest.fixture
def tools():
    events=[]
    client=Client(events)
    license=License(events)
    return load_tools(Registry(),client,license),client,license,events


def load_paypal(server=None):
    """Load only function definitions with synthetic globals; never full startup."""
    import asyncio,base64,html,sqlite3,time,zlib
    from datetime import datetime,timezone
    from starlette.requests import Request
    from starlette.responses import HTMLResponse,JSONResponse
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    try:
        from mcp.types import ToolAnnotations
    except ModuleNotFoundError:
        ToolAnnotations=types.SimpleNamespace
    tree=ast.parse((ROOT/'arn_mcp.py').read_text(encoding='utf-8'))
    names={'paypal_access_token','verify_paypal_webhook_with_api','verify_paypal_signature',
           'paypal_webhook','paypal_success','paypal_cancel','arn_create_subscription','arn_cancel_subscription',
           'paypal_subscription_details','record_verified_subscription','paypal_plan_from_id',
           'handle_paypal_delivery','create_subscription_locked','submit_subscription_creation',
           'subscription_approval_response','paypal_datetime','verified_payment_period','cancel_subscription_locked'}
    nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in names]
    scope=dict(locals())
    import tempfile, calendar
    from datetime import timedelta
    from decimal import Decimal, InvalidOperation
    from arn_paypal_store import payment_lock, PaymentBusy, creation_intent, save_creation, retire_creation, paid_period, invalidate_paid_period
    temporary = tempfile.TemporaryDirectory(prefix='arn-synthetic-paypal-', dir=ROOT.parent)
    scope.update(_temporary=temporary, LICENSE_DB=Path(temporary.name)/'synthetic.db',
                 calendar=calendar, timedelta=timedelta, Decimal=Decimal, InvalidOperation=InvalidOperation,
                 payment_lock=payment_lock, PaymentBusy=PaymentBusy,
                 creation_intent=creation_intent, save_creation=save_creation, retire_creation=retire_creation, paid_period=paid_period,
                 invalidate_paid_period=invalidate_paid_period)
    scope.update(json=json,server=server or types.SimpleNamespace(tool=lambda **kw:lambda f:f,custom_route=lambda *args,**kw:lambda f:f),
                 tool_errors=tool_errors,route_errors=route_errors,failure=failure,safe_event=safe_event,http_error=http_error,
                 requests=types.SimpleNamespace(post=Mock(),get=Mock()),
                 license_manager=Mock(),get_authenticated_user_id=lambda:'synthetic-user',
                 PAYPAL_API_BASE='https://synthetic-paypal.invalid',PAYPAL_CLIENT_ID=PRIVATE,
                 PAYPAL_CLIENT_SECRET=PRIVATE,PAYPAL_WEBHOOK_ID=PRIVATE,
                 PAYPAL_MONTHLY_PLAN_ID='synthetic-monthly',PAYPAL_YEARLY_PLAN_ID='synthetic-yearly',
                 PAYPAL_MONTHLY_AMOUNT=59,PAYPAL_YEARLY_AMOUNT=590,ARN_PUBLIC_URL='https://synthetic.invalid/arn',
                 _paypal_token=None,_paypal_token_expires_at=0,
                 verify_paypal_webhook=Mock(return_value=True),claim_paypal_event=Mock(return_value=True),
                 process_paypal_event=Mock(),complete_paypal_event=Mock(),release_paypal_event=Mock())
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'synthetic_payment_boundaries.py','exec'),scope)
    return scope
