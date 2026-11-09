"""Account/contract-bound SMTP acceptance receipts, never payment evidence.

Writer: separately sandboxed, unprivileged confirmation sender. Reader: ARN.
The receipt directory must be sender-owned and not writable by ARN or others.
No addresses, message text, keys or tokens are stored in these receipts.
"""
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import tempfile


def confirmation_reference(user_id, subscription_id, text):
    source='contract:'+hashlib.sha256((user_id+'\0'+subscription_id).encode()).hexdigest()
    return hashlib.sha256((source+'\n'+text).encode()).hexdigest()


def _directory(path, owner_uid):
    p=Path(path)
    if p.is_symlink() or not p.is_dir():raise ValueError('Receipt directory unavailable')
    if os.name=='posix':
        s=p.stat()
        if (owner_uid<=0 or s.st_uid!=owner_uid or s.st_mode&0o027
                or not s.st_mode&stat.S_ISGID):
            raise ValueError('Receipt directory permissions')
    return p


def receipt_accepted(directory, owner_uid, reference):
    if not re.fullmatch('[0-9a-f]{64}',reference):return False
    try:
        folder=_directory(directory,owner_uid)
        fd=os.open(folder/(reference+'.json'),os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
        try:
            s=os.fstat(fd)
            if not stat.S_ISREG(s.st_mode) or s.st_size>256:return False
            if os.name=='posix' and (s.st_uid!=owner_uid or s.st_mode&0o027):return False
            with os.fdopen(fd,'rb',closefd=False) as f:data=f.read(257)
        finally:os.close(fd)
        value=json.loads(data)
        return (isinstance(value,dict) and set(value)=={'version','reference','smtp_accepted'}
                and type(value['version']) is int and value['version']==1
                and value['reference']==reference and value['smtp_accepted'] is True)
    except (OSError,ValueError,TypeError):return False


def publish_acceptance(directory, owner_uid, reference):
    if not re.fullmatch('[0-9a-f]{64}',reference):raise ValueError('Invalid receipt reference')
    folder=_directory(directory,owner_uid)
    if os.name=='posix' and os.geteuid()!=owner_uid:raise ValueError('Receipt writer identity')
    if receipt_accepted(folder,owner_uid,reference):return
    fd,name=tempfile.mkstemp(prefix='.pending-',dir=folder)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(json.dumps({'version':1,'reference':reference,'smtp_accepted':True}).encode())
            f.flush();os.fsync(f.fileno())
        os.chmod(name,0o640)
        os.replace(name,folder/(reference+'.json'))
        if os.name=='posix':
            directory_fd=os.open(folder,os.O_RDONLY|getattr(os,'O_DIRECTORY',0))
            try:os.fsync(directory_fd)
            finally:os.close(directory_fd)
    finally:
        if os.path.exists(name):os.unlink(name)  # own incomplete marker, never personal records


def paid_confirmation_ready(database,user_id,subscription_lookup,acceptance_reader):
    """Legacy users bypass; new contracts require their own immutable receipt.

    Called only after the existing atomic backend result says paid=True.
    Missing/malformed state fails closed. Never creates tables or updates data.
    """
    try:
        with closing(sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True)) as c:
            c.execute('PRAGMA query_only=ON');c.execute('PRAGMA trusted_schema=OFF')
            if not c.execute("SELECT 1 FROM sqlite_schema WHERE type='table' AND name='checkout_sessions'").fetchone():
                return True  # Valid consumer database, no new contracts recorded yet.
            # No new checkout means no change to this legacy customer's access.
            if not c.execute('SELECT 1 FROM checkout_sessions WHERE user_id=? LIMIT 1',(user_id,)).fetchone():
                return True
            subscription=subscription_lookup(user_id)
            if not isinstance(subscription,dict):return False
            if subscription.get('user_id')!=user_id:return False
            sub=subscription.get('paypal_subscription_id')
            if not isinstance(sub,str) or not sub:return False
            rows=c.execute('SELECT consent_at,confirmation FROM checkout_sessions '
                           'WHERE user_id=? AND subscription_id=?',(user_id,sub)).fetchall()
            # A different, unapproved new offer does not block an older contract.
            if not rows:return True
            references={confirmation_reference(user_id,sub,text) for consent,text in rows
                        if consent and isinstance(text,str) and text}
            # Conflicting snapshots are not safe evidence for a single contract.
            return len(references)==1 and acceptance_reader(next(iter(references))) is True
    except Exception:
        return False
