"""Reused ARN-only R2 tests; no Qysley Auth modules or data."""
import asyncio
import httpx
import pytest
from unittest.mock import patch
ISSUER="https://auth.qysley.se"

@pytest.mark.parametrize('response', [httpx.Response(200, json={'active': True}), httpx.Response(200, json={'active': False}), httpx.Response(200, json={'active': 'true'}), httpx.Response(200, json={'active': True, 'extra': 1}), httpx.Response(302, headers={'Location': 'https://wrong.invalid'}), httpx.Response(503), httpx.Response(200, content=b'x' * 129, headers={'Content-Type': 'application/json'}), httpx.Response(200, content=b'{', headers={'Content-Type': 'application/json'})])
def test_arn_status_contract(response):
    import arn_auth
    real_client = httpx.AsyncClient

    def handle(request):
        assert str(request.url) == ISSUER + '/access-token-status'
        assert request.method == 'POST' and request.content == b''
        return response
    factory = lambda **kwargs: real_client(transport=httpx.MockTransport(handle), **kwargs)
    with patch.object(arn_auth.httpx, 'AsyncClient', side_effect=factory):
        actual = asyncio.run(arn_auth.access_token_is_active('synthetic-token'))
    expected = response.status_code == 200 and response.content == b'{"active":true}'
    assert actual is expected

@pytest.mark.parametrize('error', [httpx.ReadTimeout('synthetic'), httpx.ConnectError('synthetic')])
def test_arn_network_errors_closed(error):
    import arn_auth
    real_client = httpx.AsyncClient

    def handle(request):
        raise error
    with patch.object(arn_auth.httpx, 'AsyncClient', side_effect=lambda **kw: real_client(transport=httpx.MockTransport(handle), **kw)):
        assert asyncio.run(arn_auth.access_token_is_active('synthetic')) is False

def test_arn_total_deadline_fail_closed():
    import arn_auth
    real_timeout = asyncio.timeout

    async def slow(token):
        await asyncio.sleep(1)
        return True
    with patch.object(arn_auth, '_request_access_status', side_effect=slow), patch.object(arn_auth.asyncio, 'timeout', side_effect=lambda seconds: real_timeout(0.01)) as deadline:
        assert asyncio.run(arn_auth.access_token_is_active('synthetic')) is False
        deadline.assert_called_once_with(3.0)
