"""Run only as root on an ephemeral Linux CI runner. No production resources."""
import hashlib
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from library_lifecycle import initialize, revoke
from arn_library_client import content_sha256


def main():
    assert sys.platform == 'linux' and os.geteuid() == 0
    service = pwd.getpwnam('nobody')
    unrelated = pwd.getpwnam('daemon')
    assert service.pw_uid != 0 and unrelated.pw_uid != 0 and unrelated.pw_gid != service.pw_gid
    folder = Path(tempfile.mkdtemp(prefix='arn-library-permissions-'))
    try:
        content = folder / 'content'; control = folder / 'control'; trust = folder / 'trust'; code = folder / 'code'
        for d in (content, control, trust, code): d.mkdir()
        for name in ('library_lifecycle.py', 'arn_library_client.py', 'arn_client.py', 'common_cases.py', 'arn_errors.py'):
            shutil.copyfile(ROOT/name, code/name)
        row = {'library_id':'BIB-SYNTHETIC-1','version':1,'date':'','category':'El','outcome':'annat',
               'summary':'Syntetisk robot','facts':'Påhittat robotfall','reasoning':'Påhittade skäl',
               'disposition':'Påhittad utgång','companies':[],'tags':['robot'],'synthetic':True}
        approval = {'library_id':row['library_id'],'content_sha256':content_sha256(row),'status':'approved',
                    'reviewer':'SYNTHETIC','reviewed_at':'2026-11-11T00:00:00Z','legal_review':'approved',
                    'identifiability_review':'approved','legal_fidelity_review':'approved'}
        (content/'library.json').write_text(json.dumps({'schema_version':1,'records':[row]}))
        (content/'approvals.json').write_text(json.dumps({'schema_version':1,'approvals':[approval]}))
        state = initialize(control/'revocations.json', trust/'anchor.json', control/'readers.lock')
        for path in [folder, *folder.rglob('*')]:
            os.chown(path, 0, service.pw_gid)
            path.chmod(0o750 if path.is_dir() else 0o640)
        pin = hashlib.sha256((content/'approvals.json').read_bytes()).hexdigest()
        child = '''
import json,os,sys
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root/'code'))
from arn_library_client import LibraryClient
client=LibraryClient(root/'content/library.json',root/'content/approvals.json',sys.argv[2],allow_synthetic=True,
 revocations_path=root/'control/revocations.json',revocation_anchor_path=root/'trust/anchor.json',revocation_lock_path=root/'control/readers.lock')
assert len(client.search('robot'))==int(sys.argv[3])
for path in (root/'control/revocations.json',root/'trust/anchor.json',root/'control/readers.lock',root/'content/library.json'):
 try:path.open('wb')
 except PermissionError:pass
 else:raise AssertionError('Service can mutate protected state')
for path in (root/'control/forged',root/'trust/forged'):
 try:path.write_text('forged')
 except PermissionError:pass
 else:raise AssertionError('Service can replace protected state')
assert os.geteuid()!=0
print('SERVICE_ROLE_PASS')
'''
        def service_probe(expected):
            result = subprocess.run([sys.executable,'-I','-B','-c',child,str(folder),pin,str(expected)],
                                    user=service.pw_uid,group=service.pw_gid,extra_groups=[],
                                    capture_output=True,text=True,timeout=20)
            assert result.returncode == 0, result.stderr
            assert 'SERVICE_ROLE_PASS' in result.stdout
        service_probe(1)
        revoke(state,row['library_id'],'CASE-000000000000000000000001')
        service_probe(0)
        stranger = subprocess.run([sys.executable,'-I','-B','-c',
            "import pathlib,sys;pathlib.Path(sys.argv[1]).read_bytes()",str(trust/'anchor.json')],
            user=unrelated.pw_uid,group=unrelated.pw_gid,extra_groups=[],capture_output=True,text=True,timeout=10)
        assert stranger.returncode != 0 and 'PermissionError' in stranger.stderr
        print(json.dumps({'synthetic_only':True,'root_writer_nonroot_reader':True,
                          'reader_read_and_revoked_filter_passed':True,'reader_write_replace_denied':True,
                          'unrelated_read_denied':True,'new_users_created':False,'passed':True}))
    finally:
        assert folder.parent == Path(tempfile.gettempdir()) and folder.name.startswith('arn-library-permissions-')
        shutil.rmtree(folder)


if __name__ == '__main__': main()
