"""Local R7 consumer HTTP component. Not automatically registered or deployed.

Only register after approval of public legal text, recipient certificate and
configuration. Receipts acknowledge a request, never payment/cancellation.
"""
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import hashlib
import hmac
import html
import json
import os
from pathlib import Path
import secrets
import re
import sqlite3
import stat
import time
from urllib.parse import parse_qs, urlsplit

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs7
from starlette.responses import HTMLResponse, PlainTextResponse
from arn_errors import http_error


HEADERS = {'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
           'Referrer-Policy': 'same-origin',
           'Content-Security-Policy': "default-src 'none'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'"}


def technical_error(operation):
    response = http_error('backend_unavailable', operation, 503)
    response.headers.update(HEADERS)
    return response


def text_response(text, status=200, attachment=False):
    headers = dict(HEADERS)
    if attachment:
        headers['Content-Disposition'] = 'attachment; filename="arn-mottagningsbevis.txt"'
    return PlainTextResponse(text, status_code=status, headers=headers)


def contract_confirmation(*, approval_verified, plan, approved_at_utc,
                          payment_verified, terms, privacy):
    """Internal rendering only. Input must come from verified operator/server data.

    This does not verify PayPal or send a confirmation to a customer.
    """
    if approval_verified is not True or plan not in ('monthly', 'yearly'):
        raise ValueError('Verified contract data required')
    stamp = datetime.fromisoformat(approved_at_utc)
    if stamp.utcoffset() is None or type(payment_verified) is not bool:
        raise ValueError('Verified contract data required')
    price = '59 SEK per månad' if plan == 'monthly' else '590 SEK per år'
    state = 'Betalningen är verifierad.' if payment_verified else 'Betalning är inte verifierad; betald åtkomst bekräftas inte.'
    return (f'Avtalsbekräftelse — ARN Konsumenttvist MCP\nAvtal ingånget: {approved_at_utc}\n'
            f'Pris och automatisk förnyelse: {price} tills uppsägning.\n{state}\n'
            '14 dagars full ångerrätt för nytt avtal, även efter användning.\n'
            'Bekräftad uppsägning stoppar framtida förnyelser. Styrkt betald tid behålls.\n\n'
            f'Villkor — oföränderlig kopia:\n{terms}\n\nIntegritetsinformation:\n{privacy}\n')


class ConsumerHandlers:
    def __init__(self, *, approved=False, origin, database, certificate,
                 certificate_sha256, secret, terms, privacy, clock=time.time,
                 cookie_path='/consumer'):
        parsed = urlsplit(origin)
        if (approved is not True or parsed.scheme != 'https' or not parsed.hostname
                or parsed.path not in ('', '/') or parsed.username or parsed.query or parsed.fragment
                or not isinstance(secret, bytes) or len(secret) < 32 or not terms or not privacy):
            raise ValueError('Consumer publication not approved or configuration incomplete')
        if not cookie_path.startswith('/') or any(c in cookie_path for c in ('\r', '\n', ';')):
            raise ValueError('Invalid cookie scope')
        der = certificate.public_bytes(serialization.Encoding.DER)
        if not hmac.compare_digest(hashlib.sha256(der).hexdigest(), certificate_sha256):
            raise ValueError('Recipient certificate mismatch')
        now = datetime.fromtimestamp(clock(), timezone.utc)
        if not certificate.not_valid_before_utc <= now <= certificate.not_valid_after_utc:
            raise ValueError('Recipient certificate not valid')
        self.origin = origin.rstrip('/')
        self.database, self.certificate = Path(database), certificate
        self.secret, self.terms, self.privacy = secret, terms, privacy
        self.clock = clock
        self.cookie_path = cookie_path
        self.budget = []  # Global bounded admission; no retained IP/user tracking.

    allowed_tables = {'withdrawal_requests'}

    @contextmanager
    def connection(self):
        self.database.parent.mkdir(mode=0o700, parents=False, exist_ok=True)
        if os.name == 'posix':
            parent = self.database.parent.stat()
            if parent.st_uid != os.geteuid() or parent.st_mode & 0o077:
                raise ValueError()
        if self.database.is_symlink():
            raise ValueError()
        fd = os.open(self.database, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        try:
            metadata = os.fstat(fd)
            if not stat.S_ISREG(metadata.st_mode):
                raise ValueError()
            if os.name == 'posix' and (metadata.st_uid != os.geteuid() or metadata.st_mode & 0o077):
                raise ValueError()
        finally:
            os.close(fd)
        with closing(sqlite3.connect(self.database)) as conn, conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
            if tables - self.allowed_tables:
                raise ValueError()
            yield conn

    def operator_payload(self, serialized):
        return serialized.encode()

    def mac(self, value):
        return hmac.new(self.secret, value.encode(), hashlib.sha256).hexdigest()

    def admit(self):
        now = self.clock()
        self.budget = [t for t in self.budget if now - t < 60]
        if len(self.budget) >= 30:
            return False
        self.budget.append(now)
        return True

    async def information(self, request):
        return HTMLResponse('<!doctype html><html lang="sv"><meta charset="utf-8">'
                            '<title>ARN — avtalsinformation</title><h1>Avtalsinformation</h1><pre>'
                            + html.escape(self.terms) + '</pre><h2>Integritetsinformation</h2><pre>'
                            + html.escape(self.privacy) + '</pre>'
                            '<a href="withdrawal">Ångra avtalet här</a></html>', headers=HEADERS)

    async def form(self, request):
        value = str(int(self.clock())) + '.' + secrets.token_hex(24)
        token = value + '.' + self.mac('csrf:' + value)
        response = HTMLResponse('''<!doctype html><html lang="sv"><meta charset="utf-8">
<title>Ångra ARN-avtalet</title><h1>Ångra avtalet här</h1>
<p>Begäran bedöms manuellt. Du kan också kontakta arn-support@qysley.se.
Ange aldrig lösenord, tokens eller personnummer.</p>
<p><a href="information">Integritets- och avtalsinformation före inmatning</a></p>
<form method="post"><input type="hidden" name="csrf" value="''' + token + '''">
<label>Namn <input name="name" maxlength="100" required></label>
<label>E-post för kontakt (valfri om abonnemangsreferens anges) <input type="email" name="email" maxlength="254"></label>
<label>Abonnemangsreferens om känd <input name="reference" maxlength="80"></label>
<label>Mottagningsbevis <select name="receipt_format" required>
<option value="">Välj form</option><option value="text">Nedladdad textfil</option></select></label>
<button type="submit" name="confirm" value="yes">Bekräfta ånger</button></form></html>''', headers=HEADERS)
        response.set_cookie('arn_withdrawal', token, max_age=900, secure=True,
                            httponly=True, samesite='strict', path=self.cookie_path)
        return response

    async def submit(self, request):
        now = self.clock()
        if not self.admit():
            return technical_error('consumer_admission')
        if request.headers.get('origin') != self.origin:
            return text_response('Begäran nekades.', 403)
        if request.headers.get('content-type', '').split(';')[0] != 'application/x-www-form-urlencoded':
            return text_response('Ogiltigt formulär.', 400)
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 4096:
                return text_response('Formuläret är för stort.', 413)
        try:
            raw = parse_qs(body.decode('utf-8'), keep_blank_values=True, max_num_fields=6)
            if set(raw) != {'csrf', 'name', 'email', 'reference', 'receipt_format', 'confirm'} or any(len(v) != 1 for v in raw.values()):
                raise ValueError()
            values = {k: v[0].strip() for k, v in raw.items()}
            token = request.cookies.get('arn_withdrawal', '')
            if len(token) > 180 or not hmac.compare_digest(values['csrf'], token):
                raise ValueError()
            stamp, nonce, signature = token.split('.')
            if not (0 <= now - int(stamp) <= 900) or not hmac.compare_digest(signature, self.mac('csrf:' + stamp + '.' + nonce)):
                raise ValueError()
            if (values['confirm'] != 'yes' or values['receipt_format'] != 'text'
                    or not 1 <= len(values['name']) <= 100 or len(values['email']) > 254
                    or (values['email'] and not re.fullmatch(r'[^\s@<>;,]+@[^\s@<>;,]+\.[^\s@<>;,]+', values['email']))
                    or (not values['email'] and not values['reference'])
                    or len(values['reference']) > 80
                    or any(ord(c) < 32 for k in ['name', 'email', 'reference'] for c in values[k])
                    or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ ' for c in values['reference'])):
                raise ValueError()
        except (ValueError, UnicodeError):
            return text_response('Ogiltigt eller utgånget formulär.', 400)
        personal = {k: values[k] for k in ['name', 'email', 'reference']}
        serialized = json.dumps(personal, ensure_ascii=False, sort_keys=True)
        request_id, digest = self.mac('request:' + token), self.mac('payload:' + serialized)
        received = datetime.fromtimestamp(now, timezone.utc).isoformat()
        try:
            encrypted = (pkcs7.PKCS7EnvelopeBuilder().set_data(self.operator_payload(serialized))
                         .add_recipient(self.certificate)
                         .encrypt(serialization.Encoding.DER, [pkcs7.PKCS7Options.Binary]))
            with self.connection() as conn:
                conn.execute('CREATE TABLE IF NOT EXISTS withdrawal_requests (request_id TEXT PRIMARY KEY, '
                             'payload_mac TEXT NOT NULL, received_at TEXT NOT NULL, ciphertext BLOB NOT NULL, closed_at TEXT)')
                conn.execute('INSERT OR IGNORE INTO withdrawal_requests (request_id,payload_mac,received_at,ciphertext) VALUES (?,?,?,?)',
                             (request_id, digest, received, encrypted))
                saved = conn.execute('SELECT payload_mac,received_at FROM withdrawal_requests WHERE request_id=?', (request_id,)).fetchone()
                if not hmac.compare_digest(saved[0], digest):
                    return text_response('Formuläret har redan använts för en annan begäran.', 409)
                received = saved[1]
        except Exception:
            # No exception text, account data, key or form body in response/logs.
            return technical_error('consumer_store')
        return text_response('Mottagningsbevis — ARN Konsumenttvist MCP\n'
                             f'Mottaget: {received}\nÄrende: {request_id}\n'
                             f'Avtal: ARN-abonnemang {values["reference"] or "referens inte angiven"}\n'
                             'Din begäran om ånger är mottagen. Detta är inte bekräftelse på uppsägning, '
                             'återbetalning eller verifierad kontokoppling. Begäran bedöms manuellt.\n'
                             'Kontakt: arn-support@qysley.se\n', attachment=True)


def register_consumer_routes(server, handlers):
    """Explicit registration only; caller supplies approved configuration."""
    server.custom_route('/consumer/information', methods=['GET'], include_in_schema=False)(handlers.information)
    server.custom_route('/consumer/withdrawal', methods=['GET'], include_in_schema=False)(handlers.form)
    server.custom_route('/consumer/withdrawal', methods=['POST'], include_in_schema=False)(handlers.submit)
