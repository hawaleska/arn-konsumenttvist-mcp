import asyncio
import json
import logging

import httpx
import pytest

sdk=pytest.importorskip('mcp.server.mcpserver')
from conftest import load_tools,Client,License,PRIVATE,INTERNAL_URL
from test_tool_response_boundaries import ARGS


def result_json(response):
    assert response.status_code==200
    if response.headers.get('content-type','').startswith('text/event-stream'):
        return json.loads(next(line[6:] for line in response.text.splitlines() if line.startswith('data: ')))
    return response.json()


@pytest.mark.parametrize('mode',['success','partial_failure','payment_required','direct_failure'])
def test_real_mcp_wire_serialization(mode,caplog,capsys):
    caplog.set_level(logging.INFO)
    events=[]
    backend=Client(events);license=License(events)
    backend.failure=mode in ('partial_failure','direct_failure')
    backend.search_failure=mode=='direct_failure'
    license.allowed=mode!='payment_required'
    server=sdk.MCPServer(name='synthetic-r3-contract',version='test-only')
    load_tools(server,backend,license)
    app=server.streamable_http_app()
    names=list(ARGS) if mode!='partial_failure' else ['arn_search_and_read','arn_search_company_and_read']
    if mode=='direct_failure':names=['arn_search','arn_get_decision']
    async def run():
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://localhost:8000') as client:
                headers={'Accept':'application/json, text/event-stream'}
                response=await client.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'synthetic-r3-client','version':'test-only'}}})
                assert response.status_code==200
                headers['Mcp-Session-Id']=response.headers['mcp-session-id']
                headers['MCP-Protocol-Version']='2025-11-25'
                response=await client.post('/mcp',headers=headers,json={'jsonrpc':'2.0','method':'notifications/initialized'})
                assert response.status_code==202
                listing=result_json(await client.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':2,'method':'tools/list'}))
                assert {item['name'] for item in listing['result']['tools']}==set(ARGS)
                for i,name in enumerate(names,3):
                    response=await client.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':i,'method':'tools/call','params':{'name':name,'arguments':ARGS[name]}})
                    assert PRIVATE not in response.text and INTERNAL_URL not in response.text
                    result=result_json(response)['result']
                    if mode=='direct_failure':
                        assert result.get('isError') is True
                        message=result['content'][0]['text']
                        assert message.startswith('Error executing tool '+name+': ')
                        public=json.loads(message.split(': ',1)[1])
                        assert public['error']=='result_unavailable' and len(public['reference_id'])==32
                        assert public['reference_id'] in caplog.text
                        continue
                    assert not result.get('isError',False)
                    text=[json.loads(item['text']) for item in result['content'] if item['type']=='text']
                    assert text and 'retrieved_at' in text[0]
                    if 'structuredContent' in result:
                        assert result['structuredContent']==text[0]
    asyncio.run(run())
    assert PRIVATE not in caplog.text and INTERNAL_URL not in caplog.text
    captured=capsys.readouterr()
    assert PRIVATE not in captured.out+captured.err and INTERNAL_URL not in captured.out+captured.err
