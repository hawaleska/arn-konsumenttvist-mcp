import ast
import asyncio
import copy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SIX={'arn_search','arn_get_decision','arn_search_and_read','arn_search_company','arn_search_company_and_read','arn_similar_cases'}
EIGHT=SIX|{'arn_create_subscription','arn_cancel_subscription'}
NOTE=' Anropet kan förbruka en fri användning, även vid upprepning.'

def tools(tree):
    return {n.name:n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in EIGHT}

def registration(n):
    return next(d for d in n.decorator_list if isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr=='tool')

old=ast.parse((ROOT/'baseline/arn_mcp.py').read_bytes())
new=ast.parse((ROOT/'arn_mcp.py').read_bytes())
assert set(tools(old))==set(tools(new))==EIGHT
normalized=copy.deepcopy(new)
for name,n in tools(normalized).items():
    actual=registration(n);original=registration(tools(old)[name])
    kw={k.arg:k.value for k in actual.keywords}
    okw={k.arg:k.value for k in original.keywords}
    expected={k.arg:ast.literal_eval(k.value) for k in okw['annotations'].keywords}
    expected['openWorldHint']=True
    if name in SIX:expected.update(readOnlyHint=False,idempotentHint=False)
    assert {k.arg:ast.literal_eval(k.value) for k in kw['annotations'].keywords}==expected
    assert ast.literal_eval(kw['description'])==ast.literal_eval(okw['description'])+(NOTE if name in SIX else '')
    for k in actual.keywords:
        if k.arg in ('annotations','description'):k.value=copy.deepcopy(okw[k.arg])
for name,n in tools(new).items():
    before=tools(old)[name]
    assert ast.dump(n.args)==ast.dump(before.args)
    assert ast.dump(n.returns)==ast.dump(before.returns)
# R9-R11 intentionally change bodies/startup. R5 metadata and full wire
# input schemas remain compared below; body scope has a separate AST test.
print('PASS: annotations/descriptions for all 8; all eight argument/return contracts preserved',flush=True)

if __name__=='__main__':
    import importlib.metadata
    import httpx
    from mcp.server.mcpserver import MCPServer
    from mcp.types import ToolAnnotations
    print('Python/SDK:',__import__('sys').version.split()[0],importlib.metadata.version('mcp'),flush=True)
    async def listing(tree):
        server=MCPServer(name='r5-synthetic-metadata',version='test-only')
        identity=lambda *_:lambda fn:fn
        namespace={'server':server,'ToolAnnotations':ToolAnnotations,'public_response':identity,'tool_errors':identity}
        # Actual definitions/signatures/decorators only. No module startup or function invocation.
        module=ast.Module(body=[copy.deepcopy(n) for n in tools(tree).values()],type_ignores=[])
        exec(compile(module,'synthetic-tool-definitions','exec'),namespace)
        app=server.streamable_http_app()
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://localhost:8000') as client:
                headers={'Accept':'application/json, text/event-stream'}
                async def call(body):
                    r=await client.post('/mcp',headers=headers,json=body)
                    assert r.status_code==200
                    data=json.loads(next(x[6:] for x in r.text.splitlines() if x.startswith('data: '))) if r.headers.get('content-type','').startswith('text/event-stream') else r.json()
                    return r,data
                r,_=await call({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'r5-synthetic','version':'test-only'}}})
                headers['Mcp-Session-Id']=r.headers['mcp-session-id'];headers['MCP-Protocol-Version']='2025-11-25'
                r=await client.post('/mcp',headers=headers,json={'jsonrpc':'2.0','method':'notifications/initialized'})
                assert r.status_code==202
                _,data=await call({'jsonrpc':'2.0','id':2,'method':'tools/list'})
                return {t['name']:t for t in data['result']['tools']}
    async def run():
        baseline=await listing(old);candidate=await listing(new)
        assert set(baseline)==set(candidate)==EIGHT
        for name,item in candidate.items():
            expected=copy.deepcopy(baseline[name])
            expected['annotations']['openWorldHint']=True
            if name in SIX:
                expected['annotations'].update(readOnlyHint=False,idempotentHint=False)
                expected['description']+=NOTE
            assert item==expected,name
        print('PASS: real SDK tools/list wire metadata for all 8; input schemas and every other field unchanged',flush=True)
    asyncio.run(run())
