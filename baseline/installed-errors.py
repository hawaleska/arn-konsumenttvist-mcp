"""Small, allowlisted error contract; never format untrusted diagnostics."""

from dataclasses import dataclass
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import json
import logging
import re
import uuid

LOGGER = logging.getLogger('arn.errors')
_REFERENCE = ContextVar('arn_error_reference', default=None)
MESSAGES = {
    'decision_unavailable': 'Beslutet kunde inte hämtas.',
    'result_unavailable': 'Resultatet kunde inte hämtas.',
    'backend_unavailable': 'Tjänsten kunde inte nås. Försök igen senare.',
    'backend_invalid_response': 'Tjänstens svar kunde inte behandlas.',
    'backend_invalid_request': 'Begäran kunde inte behandlas.',
    'backend_access_denied': 'Tjänsten kunde inte behandla begäran.',
    'payment_required': 'Fortsatt användning kräver en aktiv prenumeration.',
    'already_subscribed': 'Du har redan en aktiv prenumeration. Avsluta den befintliga prenumerationen innan du tecknar en ny.',
    'invalid_plan': "Plan måste vara 'monthly' eller 'yearly'.",
    'no_active_subscription': 'Du har ingen aktiv prenumeration att avsluta.',
    'paypal_cancel_failed': 'PayPal kunde inte avsluta prenumerationen. Försök igen senare.',
    'paypal_cancel_error': 'Ett fel uppstod när prenumerationen skulle avslutas.',
    'invalid_request': 'Begäran kunde inte behandlas.',
    'signature_invalid': 'Begäran kunde inte verifieras.',
    'missing_event_id': 'Begäran saknar nödvändiga uppgifter.',
    'webhook_processing_failed': 'Begäran kunde inte behandlas. Försök igen senare.',
}
OPERATIONS = frozenset((
    'public_response', 'license_request', 'similar_cases',
    'arn_search', 'arn_get_decision', 'arn_search_and_read', 'arn_search_company',
    'arn_search_company_and_read', 'arn_similar_cases', 'arn_create_subscription',
    'arn_cancel_subscription', 'paypal_access_token', 'verify_paypal_webhook_with_api',
    'verify_paypal_signature', 'verify_paypal_webhook', 'get_user_id_from_subscription',
    'store_subscription_if_possible', 'process_paypal_event', 'paypal_webhook',
    'paypal_success', 'paypal_cancel',
))
BUSINESS_ERRORS = frozenset(('already_subscribed','invalid_plan','no_active_subscription',
                            'paypal_cancel_failed','paypal_cancel_error'))
_BUSINESS_FIELDS = {
    'already_subscribed': {'subscription_id': str, 'plan': str},
    'paypal_cancel_failed': {'status_code': int},
}


@dataclass(frozen=True, slots=True)
class _Failure:
    code: str
    reference_id: str

    def public(self):
        return {'error': self.code, 'message': MESSAGES[self.code], 'reference_id': self.reference_id}


def _operation(value):
    return value if type(value) is str and value in OPERATIONS else 'public_response'


@contextmanager
def error_context():
    token=_REFERENCE.set(_REFERENCE.get() or uuid.uuid4().hex)
    try:
        yield
    finally:
        _REFERENCE.reset(token)


def safe_event(operation, outcome='observed', *, status=None):
    # This API accepts classification only, never body/headers/exception/identifiers.
    record={'operation':_operation(operation),
            'outcome':outcome if type(outcome) is str and outcome in ('observed','completed','rejected','duplicate','ignored') else 'observed'}
    if type(status) is int and 100 <= status <= 599:
        record['http_status']=status
    LOGGER.info(json.dumps(record,ensure_ascii=True))


def _trusted(value):
    if (isinstance(value,_Failure) and type(value.code) is str and value.code in MESSAGES
            and type(value.reference_id) is str and re.fullmatch('[0-9a-f]{32}',value.reference_id)):
        return value
    if isinstance(value,BaseException):
        stored=getattr(value,'_arn_safe_failure',None)
        if isinstance(stored,_Failure):
            return _trusted(stored)
    return None


def failure(code, operation, error=None, *, status=None):
    if type(code) is not str or code not in MESSAGES:
        code='result_unavailable'
    previous=_trusted(error)
    if previous is not None and previous.code==code:
        return previous
    result=_Failure(code,previous.reference_id if previous else _REFERENCE.get() or uuid.uuid4().hex)
    record={'error':code,'reference_id':result.reference_id,'operation':_operation(operation)}
    if type(status) is int and 100 <= status <= 599:
        record['http_status']=status
    LOGGER.warning(json.dumps(record,ensure_ascii=True))
    # Preserve a reference across existing catch/rethrow paths, without reading str(exc).
    if isinstance(error,Exception):
        try:error._arn_safe_failure=result
        except Exception:pass
    return result


def public_error(value, code, operation):
    return failure(code,operation,value).public()


def safe_exception(category, code, operation, error=None, *, status=None):
    if category not in (ValueError,PermissionError,RuntimeError):
        category=RuntimeError
    result=failure(code,operation,error,status=status)
    exception=category(MESSAGES[result.code])
    exception._arn_safe_failure=result
    return exception


def backend_errors(function):
    @wraps(function)
    def wrapped(*args,**kwargs):
        try:return function(*args,**kwargs)
        except Exception as exc:
            previous=_trusted(exc)
            category=ValueError if isinstance(exc,ValueError) else PermissionError if isinstance(exc,PermissionError) else RuntimeError
            code=previous.code if previous else 'backend_unavailable'
            raise safe_exception(category,code,'license_request',exc) from None
    return wrapped


def raise_tool_error(error, operation):
    from mcp.server.mcpserver.exceptions import ToolError
    previous=_trusted(error)
    result=previous or failure('result_unavailable',operation,error)
    raise ToolError(json.dumps(result.public(),ensure_ascii=False)) from None


def tool_errors(operation):
    def decorate(function):
        @wraps(function)
        def wrapped(*args,**kwargs):
            with error_context():
                try:
                    result=function(*args,**kwargs)
                    if type(result) is dict and 'error' in result:
                        previous=_trusted(result['error'])
                        code=previous.code if previous else result['error']
                        if type(code) is not str or code not in BUSINESS_ERRORS:
                            return public_error(previous,'result_unavailable',operation)
                        public=public_error(previous,code,operation)
                        # Preserve documented domain-error fields, never a generic error bag.
                        for key, kind in _BUSINESS_FIELDS.get(code,{}).items():
                            if type(result.get(key)) is kind:
                                public[key]=result[key]
                        return public
                    return result
                except Exception as exc:
                    raise_tool_error(exc,operation)
        return wrapped
    return decorate


def http_error(code, operation, status, error=None):
    from starlette.responses import JSONResponse
    return JSONResponse(public_error(error,code,operation),status_code=status,
                        headers={'Cache-Control':'no-store'})


def route_errors(operation):
    def decorate(function):
        @wraps(function)
        async def wrapped(*args,**kwargs):
            with error_context():
                try:return await function(*args,**kwargs)
                except Exception as exc:
                    return http_error('webhook_processing_failed' if operation=='paypal_webhook' else 'result_unavailable',operation,500,exc)
        return wrapped
    return decorate
