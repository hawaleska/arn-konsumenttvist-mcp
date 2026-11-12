import ast,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_version_consistent_in_registry_server_readme_and_changelog():
 m=json.loads((ROOT/'server.json').read_text(encoding='utf-8'));assert m['version']=='1.0.4'
 tree=ast.parse((ROOT/'arn_mcp.py').read_bytes())
 server=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='server' for t in n.targets))
 assert next(k.value.value for k in server.value.keywords if k.arg=='version')==m['version']
 assert '1.0.4' in (ROOT/'README.md').read_text(encoding='utf-8').splitlines()[0]
 assert '## 1.0.4' in (ROOT/'CHANGELOG.md').read_text(encoding='utf-8')
def test_registry_description_and_auth_transport_constraints():
 m=json.loads((ROOT/'server.json').read_text(encoding='utf-8'))
 assert 1<=len(m['description'])<=100
 assert m['remotes'][0]['type']=='streamable-http' and m['remotes'][0]['url']=='https://mcp.qysley.se/arn/mcp'
 h=m['remotes'][0]['headers'][0];assert h['name']=='Authorization' and h['isSecret'] is True and 'value' not in h
 assert m['repository']['url']=='https://github.com/hawaleska/arn-konsumenttvist-mcp'
def test_all_runtime_files_match_independently_verified_live_source():
 live=json.loads((ROOT/'tests/production_contracts_20261112.json').read_text(encoding='utf-8'))
 for name,digest in live['file_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
