import asyncio
import json
import logging

import httpx
import pytest

sdk=pytest.importorskip('mcp.server.mcpserver')
from conftest import load_paypal,PRIVATE,INTERNAL_URL
from test_mcp_serialization import result_json
from test_error_contract import assert_clean


@pytest.mark.parametrize('name',['arn_create_subscription','arn_cancel_subscription'])
def test_payment_tool_error_keeps_iserror_and_reference_on_real_sdk(name,caplog,capsys):
    caplog.set_level(logging.INFO)
    server=sdk.MCPServer(name='synthetic-r4-errors',version='test-only')
    scope=load_paypal(server)
    scope['license_manager'].get_active_subscription.side_effect=RuntimeError(INTERNAL_URL+' BEARER_CANARY')
    app=server.streamable_http_app()
    async def run():
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://localhost:8000') as client:
                headers={'Accept':'application/json, text/event-stream'}
                r=await client.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'synthetic-r4','version':'test-only'}}})
                assert r.status_code==200
                headers['Mcp-Session-Id']=r.headers['mcp-session-id']
                headers['MCP-Protocol-Version']='2025-11-25'
                await client.post('/mcp',headers=headers,json={'jsonrpc':'2.0','method':'notifications/initialized'})
                r=await client.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':name,'arguments':{}}})
                result=result_json(r)['result']
                assert result['isError'] is True
                message=result['content'][0]['text']
                assert message.startswith('Error executing tool '+name+': ')
                public=json.loads(message.split(': ',1)[1])
                assert public['error']=='result_unavailable'
                assert public['reference_id'] in caplog.text
                assert_clean(r.text)
    asyncio.run(run())
    assert_clean(caplog.text)
    captured=capsys.readouterr()
    assert_clean(captured.out+captured.err)
