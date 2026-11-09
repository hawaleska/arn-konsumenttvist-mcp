"""Read-only ARN disclosure restriction projection. No Auth/payment writes.

Root publishes an approved projection outside source-data backups. Runtime
readers cannot edit it. Decisions take effect for newly admitted operations;
activation must quiesce existing ARN work, not promise to recall sent data.
"""
import hashlib,json,os,re,stat
from pathlib import Path


class DisclosureBlocked(RuntimeError):
    def __init__(self,reason):
        self.reason=reason;super().__init__('ARN disclosure blocked')


def subject_reference(subject):
    if not isinstance(subject,str) or not subject or len(subject)>512 or '\0' in subject:
        raise DisclosureBlocked('unavailable')
    return hashlib.sha256(('ARN-disclosure\0'+subject).encode()).hexdigest()


def revision_for(source_digest,blocked_subjects):
    return hashlib.sha256(json.dumps({'source_digest':source_digest,'blocked_subjects':blocked_subjects},
        sort_keys=True,separators=(',',':')).encode()).hexdigest()


def validate_projection(value):
    if (not isinstance(value,dict) or set(value)!={'version','source_digest','blocked_subjects','revision'}
            or type(value['version']) is not int or value['version']!=1
            or not isinstance(value['source_digest'],str) or not re.fullmatch('[a-f0-9]{64}',value['source_digest'])
            or not isinstance(value['blocked_subjects'],list) or len(value['blocked_subjects'])>10000
            or any(not isinstance(x,str) or not re.fullmatch('[a-f0-9]{64}',x) for x in value['blocked_subjects'])
            or value['blocked_subjects']!=sorted(set(value['blocked_subjects']))
            or value['revision']!=revision_for(value['source_digest'],value['blocked_subjects'])):
        raise DisclosureBlocked('unavailable')
    return value


class DisclosurePolicy:
    def __init__(self,path,*,owner_uid=0):
        self.path=Path(path);self.owner_uid=owner_uid
        if not self.path.is_absolute():raise DisclosureBlocked('unavailable')

    def _read(self):
        try:
            parent=self.path.parent
            if self.path.is_symlink() or parent.is_symlink():raise ValueError()
            if os.name=='posix':
                p=parent.stat()
                if p.st_uid!=self.owner_uid or p.st_mode&0o027:raise ValueError()
            fd=os.open(self.path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
            try:
                s=os.fstat(fd)
                if not stat.S_ISREG(s.st_mode) or s.st_size>1000000:raise ValueError()
                if os.name=='posix' and (s.st_uid!=self.owner_uid or s.st_mode&0o027):raise ValueError()
                with os.fdopen(fd,'rb',closefd=False) as f:raw=f.read(1000001)
            finally:os.close(fd)
            return validate_projection(json.loads(raw))
        except Exception:
            raise DisclosureBlocked('unavailable') from None
    def validate_available(self):
        return {'revision':self._read()['revision'],'available':True}

    def require_disclosure(self,subject):
        ref=subject_reference(subject);value=self._read()
        if ref in value['blocked_subjects']:raise DisclosureBlocked('restricted')
        return {'revision':value['revision'],'permitted':True}


def policy_from_environment(*,required=False):
    path=os.getenv('ARN_DISCLOSURE_POLICY')
    if not path:
        if required:raise DisclosureBlocked('unavailable')
        return None  # Legacy, not an activated R7 deployment.
    return DisclosurePolicy(path)  # Production owner is always root, no env bypass.
