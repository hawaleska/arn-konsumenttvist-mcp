"""Private local PayPal coordination. No credentials or webhook bodies are stored.

All payment handlers use one OS lock. The kernel releases it on process death;
there is no lease which can expire while an old handler is still writing.
"""
from contextlib import contextmanager, closing
import os
import sqlite3
import uuid


class PaymentBusy(RuntimeError):
    pass


@contextmanager
def payment_connection(database):
    # New stores must be private before SQLite writes any approval URLs.
    fd = os.open(database, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    os.close(fd)
    with closing(sqlite3.connect(database)) as conn:
        with conn:
            yield conn


@contextmanager
def payment_lock(database):
    path = str(database) + '.paypal.lock'
    flags = os.O_RDWR | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(path, flags, 0o600)
    locked = False
    try:
        if os.name == 'nt':
            import msvcrt
            if os.fstat(fd).st_size == 0:
                os.write(fd, b'0')
            os.lseek(fd, 0, os.SEEK_SET)
            try:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            except OSError:
                raise PaymentBusy('Payment processing busy.') from None
        else:
            import fcntl
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise PaymentBusy('Payment processing busy.') from None
        locked = True
        yield
    finally:
        if locked:
            if os.name == 'nt':
                import msvcrt
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def creation_intent(database, user_id, plan):
    """Must run under payment_lock. Never automatically repeat an uncertain POST."""
    with payment_connection(database) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS paypal_creation_intents (
            user_id TEXT NOT NULL, plan TEXT NOT NULL,
            request_id TEXT PRIMARY KEY, state TEXT NOT NULL,
            subscription_id TEXT, approval_url TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS paypal_one_open_creation ON paypal_creation_intents(user_id) WHERE state != 'retired'")
        conn.execute('''INSERT OR IGNORE INTO paypal_creation_intents
            (user_id, plan, request_id, state) VALUES (?, ?, ?, 'prepared')''',
            (user_id, plan, uuid.uuid4().hex))
        conn.row_factory = sqlite3.Row
        row = dict(conn.execute("SELECT * FROM paypal_creation_intents WHERE user_id=? AND state != 'retired'", (user_id,)).fetchone())
        return row


def save_creation(database, user_id, state, subscription_id=None, approval_url=None):
    with payment_connection(database) as conn:
        conn.execute('''UPDATE paypal_creation_intents SET state=?,
            subscription_id=COALESCE(?, subscription_id),
            approval_url=COALESCE(?, approval_url) WHERE user_id=? AND state != 'retired' ''',
            (state, subscription_id, approval_url, user_id))


def retire_creation(database, request_id):
    with payment_connection(database) as conn:
        conn.execute("UPDATE paypal_creation_intents SET state='retired' WHERE request_id=? AND state='registered'", (request_id,))


def paid_period(database, subscription_id, verified_until=None):
    """Only boundaries independently verified by the new payment rule belong here.

    Historical D1 expires_at values are deliberately not imported as evidence.
    """
    with payment_connection(database) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS paypal_verified_periods (
            subscription_id TEXT PRIMARY KEY, paid_until TEXT NOT NULL,
            valid INTEGER NOT NULL DEFAULT 1)''')
        if verified_until is not None:
            conn.execute('''INSERT INTO paypal_verified_periods(subscription_id, paid_until) VALUES (?, ?)
                ON CONFLICT(subscription_id) DO UPDATE SET paid_until=excluded.paid_until, valid=1''',
                (subscription_id, verified_until))
        row = conn.execute('SELECT paid_until FROM paypal_verified_periods WHERE subscription_id=? AND valid=1',
                           (subscription_id,)).fetchone()
        return row[0] if row else None


def invalidate_paid_period(database, subscription_id):
    # Keep the evidence boundary, but never use refunded/reversed evidence.
    with payment_connection(database) as conn:
        conn.execute('UPDATE paypal_verified_periods SET valid=0 WHERE subscription_id=?', (subscription_id,))
