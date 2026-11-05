import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import pytest
from conftest import ROOT

def test_manifest_component_version_and_safe_endpoints_agree():
    manifest=json.loads((ROOT/'server.json').read_text(encoding='utf-8'))
    tree=ast.parse((ROOT/'arn_mcp.py').read_text(encoding='utf-8'))
    server=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='server' for t in n.targets))
    assert next(ast.literal_eval(k.value) for k in server.keywords if k.arg=='version')==manifest['version']=='1.0.4'
    assert manifest['remotes'][0]['url']=='https://mcp.qysley.se/arn/mcp'
    assert '1.0.4' in (ROOT/'CHANGELOG.md').read_text(encoding='utf-8')

def test_legacy_dedup_storage_functions_unchanged():
    def nodes(path):
        return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef)}
    old=nodes(ROOT/'baseline/arn_mcp.py');new=nodes(ROOT/'arn_mcp.py')
    for name in ('init_paypal_webhook_store','claim_paypal_event','complete_paypal_event','release_paypal_event'):
        assert old[name]==new[name]

def test_gitignore_keeps_secrets_private_and_sql_tests_visible(tmp_path):
    git=shutil.which('git')
    if not git:pytest.skip('git unavailable: ignore integration not verified')
    (tmp_path/'.gitignore').write_bytes((ROOT/'.gitignore').read_bytes())
    env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull)
    def run(*args,**kwargs):return subprocess.run([git,'-C',str(tmp_path),*args],env=env,capture_output=True,text=True,check=True,**kwargs)
    templates=tmp_path/'empty-templates';templates.mkdir()
    run('init','--quiet','--template='+str(templates))
    blocked={'.env','.env.production','.env.test','local-private/dump.sql','test.sqlite','state.db','state.db-wal'}
    visible={'.env.example','migrations/001.sql','tests/test_quota.py'}
    result=run('check-ignore','--no-index','--stdin','-z',input='\0'.join(sorted(blocked|visible))+'\0')
    assert set(result.stdout.rstrip('\0').split('\0'))==blocked
