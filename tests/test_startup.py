"""Real module/startup/SDK path, isolated source copy and synthetic config."""
import os
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
from library_lifecycle import initialize

def test_full_import_streamable_startup_and_auth_smoke(tmp_path):
    root=Path(__file__).resolve().parents[1]
    for p in root.glob('*.py'):
        shutil.copyfile(p,tmp_path/p.name)
    shutil.copytree(root/'library',tmp_path/'library')
    control=initialize(tmp_path/'control/revocations.json',tmp_path/'trust/anchor.json',tmp_path/'control/readers.lock')
    assert not (tmp_path/'.env').exists()
    code=r'''
import sys,runpy,asyncio
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import httpx,requests,urllib.request,uvicorn
def forbidden(*args,**kwargs):raise AssertionError('Unexpected external network request')
requests.sessions.Session.request=forbidden
urllib.request.urlopen=forbidden
httpx.HTTPTransport.handle_request=forbidden
httpx.AsyncHTTPTransport.handle_async_request=forbidden
seen=[]
async def serve(self,*args,**kwargs):
    app=self.config.app
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://localhost:8000') as c:
            r=await c.get('/.well-known/oauth-protected-resource/arn')
            assert r.status_code==200
            assert r.json()['resource']=='https://mcp.qysley.se/arn'
            r=await c.post('/mcp',json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{}})
            assert r.status_code==401 and r.headers['www-authenticate'].startswith('Bearer ')
    seen.append(True)
uvicorn.Server.serve=serve
state=runpy.run_path(str(Path(sys.argv[1])/'arn_mcp.py'),run_name='__main__')
assert state['server']._lowlevel_server.version=='1.0.4'
assert seen==[True]
assert (Path(sys.argv[1])/'arn_license.db').is_file()
print('FULL_STARTUP_REAL_SDK_ASGI_SMOKE_PASS')
'''
    env={k:os.environ[k] for k in ('SYSTEMROOT','WINDIR','PATH','TEMP','TMP') if k in os.environ}
    env.update(ARN_D1_API_URL='https://synthetic-backend.invalid',ARN_D1_API_SECRET='synthetic-test-only',
               PAYPAL_ENV='sandbox',PAYPAL_CLIENT_ID='synthetic-client',PAYPAL_CLIENT_SECRET='synthetic-secret',
               PAYPAL_WEBHOOK_ID='synthetic-webhook',PAYPAL_MONTHLY_PLAN_ID='synthetic-monthly',
               PAYPAL_YEARLY_PLAN_ID='synthetic-yearly',MCP_TRANSPORT='streamable-http')
    env.update(ARN_LIBRARY_APPROVALS_SHA256=hashlib.sha256((tmp_path/'library/approvals.json').read_bytes()).hexdigest(),
               ARN_LIBRARY_REVOCATIONS=str(control.journal),ARN_LIBRARY_REVOCATION_ANCHOR=str(control.anchor),
               ARN_LIBRARY_REVOCATION_LOCK=str(control.lock))
    result=subprocess.run([sys.executable,'-I','-B','-c',code,str(tmp_path)],cwd=tmp_path,env=env,capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stdout+result.stderr
    assert 'FULL_STARTUP_REAL_SDK_ASGI_SMOKE_PASS' in result.stdout
