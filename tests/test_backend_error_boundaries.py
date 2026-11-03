import io
import json
from urllib.error import HTTPError,URLError
from unittest.mock import patch

import pytest

from arn_license import LicenseManager
from arn_errors import failure
from conftest import PRIVATE,INTERNAL_URL
from test_error_contract import assert_clean


def manager():
    result=object.__new__(LicenseManager)
    result.api_url='https://synthetic-backend.invalid/'
    result.api_secret='BEARER_CANARY'
    return result


@pytest.mark.parametrize('status,category,code',[(400,ValueError,'backend_invalid_request'),(401,PermissionError,'backend_access_denied'),(403,PermissionError,'backend_access_denied'),(500,RuntimeError,'backend_unavailable')])
def test_backend_http_statuses_preserve_categories(status,category,code,caplog):
    error=HTTPError(INTERNAL_URL,status,'RAW_BODY_CANARY',{},io.BytesIO(b'BEARER_CANARY RAW_BODY_CANARY'))
    with patch('arn_license.urlopen',side_effect=error):
        with pytest.raises(category) as raised:manager().user_id_from_api_key('synthetic-key')
    assert raised.value._arn_safe_failure.code==code
    assert raised.value.__suppress_context__
    assert_clean(str(raised.value)+caplog.text)


@pytest.mark.parametrize('error',[URLError(INTERNAL_URL),TimeoutError('BEARER_CANARY'),UnicodeError('RAW_BODY_CANARY')])
def test_backend_transport_failures_safe(error,caplog):
    with patch('arn_license.urlopen',side_effect=error):
        with pytest.raises(RuntimeError) as raised:manager().check('synthetic-user')
    assert raised.value._arn_safe_failure.code==('backend_invalid_response' if isinstance(error,UnicodeError) else 'backend_unavailable')
    assert_clean(str(raised.value)+caplog.text)


class Response:
    status=200
    def __init__(self,data):self.data=data
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self):return self.data


@pytest.mark.parametrize('body',[b'RAW_BODY_CANARY',b'{"ok":false,"error":"BEARER_CANARY"}',b'["RAW_BODY_CANARY"]'])
def test_backend_bad_payloads_are_neutral(body,caplog):
    with patch('arn_license.urlopen',return_value=Response(body)):
        with pytest.raises(RuntimeError) as raised:manager().check('synthetic-user')
    assert raised.value._arn_safe_failure.code=='backend_invalid_response'
    assert_clean(str(raised.value)+caplog.text)


def test_successful_backend_actions_and_payload_preserved():
    expected={'allowed':True,'remaining':3}
    with patch('arn_license.urlopen',return_value=Response(json.dumps(expected).encode())) as request:
        assert manager().check('synthetic-user')==expected
        sent=json.loads(request.call_args.args[0].data)
        assert sent=={'action':'check','user_id':'synthetic-user'}


@pytest.mark.parametrize('action',['get_subscription','get_subscription_by_paypal_id','get_active_subscription'])
def test_legitimate_missing_subscription_remains_none(action,caplog):
    with patch('arn_license.urlopen',return_value=Response(b'null')):
        assert manager()._request(action,user_id='synthetic-user') is None
    assert not caplog.records


def test_null_is_not_accepted_as_positive_auth_or_quota_response(caplog):
    with patch('arn_license.urlopen',return_value=Response(b'null')):
        with pytest.raises(RuntimeError):manager().user_id_from_api_key('synthetic-key')
    assert_clean(caplog.text)
