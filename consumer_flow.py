"""R7 customer-path integration. Explicit mounting only; no provider calls."""
from datetime import datetime, timezone
from email.message import EmailMessage
from email import policy
from contextlib import closing
import hashlib
import html
import json
import secrets
import sqlite3
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from starlette.responses import HTMLResponse, Response
from consumer_handlers import ConsumerHandlers, HEADERS, text_response, technical_error, register_consumer_routes
from consumer_confirmation_gate import paid_confirmation_ready


class ConsumerFlow(ConsumerHandlers):
    allowed_tables = {'withdrawal_requests', 'checkout_sessions'}

    def __init__(self, *, public_base_url, plan_ids, lookup_approval, withdrawal_instructions,
                 paypal_host, acceptance_reader=None, **kwargs):
        super().__init__(**kwargs)
        base = urlsplit(public_base_url)
        if (base.scheme + '://' + base.netloc != self.origin or base.query or base.fragment
                or set(plan_ids) != {'monthly', 'yearly'} or not all(plan_ids.values())
                or not callable(lookup_approval) or not withdrawal_instructions
                or paypal_host not in {'www.paypal.com', 'www.sandbox.paypal.com'}):
            raise ValueError('Incomplete consumer integration')
        self.base = public_base_url.rstrip('/')
        self.plan_ids, self.lookup_approval = plan_ids, lookup_approval
        self.instructions = withdrawal_instructions
        self.paypal_host = paypal_host
        self.cookie_path = (base.path.rstrip('/') + '/consumer')
        self.acceptance_reader = acceptance_reader or (lambda reference: False)

    def paid_confirmation_ready(self, user_id, subscription_lookup):
        return paid_confirmation_ready(self.database, user_id, subscription_lookup, self.acceptance_reader)

    def _schema(self, conn):
        conn.row_factory = __import__('sqlite3').Row
        conn.execute('''CREATE TABLE IF NOT EXISTS checkout_sessions (
            cap_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL, subscription_id TEXT NOT NULL,
            plan TEXT NOT NULL, created REAL NOT NULL, terms TEXT NOT NULL,
            privacy TEXT NOT NULL, instructions TEXT NOT NULL, consent_at TEXT,
            confirmation TEXT)''')

    def wrap_approval(self, user_id, plan, subscription_id, approval_url):
        if not user_id or plan not in self.plan_ids or not subscription_id:
            raise ValueError('Invalid offer')
        # The approval URL stays in the existing protected creation-intent store.
        self._paypal_url(approval_url)
        token = secrets.token_hex(32)
        with self.connection() as conn:
            self._schema(conn)
            conn.execute('INSERT INTO checkout_sessions VALUES (?,?,?,?,?,?,?,?,NULL,NULL)',
                         (self.mac('cap:' + token), user_id, subscription_id, plan,
                          self.clock(), self.terms, self.privacy, self.instructions))
        # A fragment is not sent in the HTTP request URL or Referer.
        return self.base + '/consumer/checkout#' + token

    def _paypal_url(self, value):
        parsed = urlsplit(value or '')
        if (parsed.scheme != 'https' or parsed.hostname != self.paypal_host
                or parsed.username or parsed.password or parsed.port not in (None, 443) or parsed.fragment):
            raise ValueError('Invalid provider destination')
        return value

    def _session(self, conn, token):
        if len(token) != 64 or any(c not in '0123456789abcdef' for c in token):
            return None
        self._schema(conn)
        row = conn.execute('SELECT * FROM checkout_sessions WHERE cap_hash=?',
                           (self.mac('cap:' + token),)).fetchone()
        if row is None or not 0 <= self.clock() - row['created'] <= 86400:
            return None
        return row

    def _checkout_headers(self):
        # Chromium enforces form-action on a POST's redirect too. Permit only
        # the already validated provider origin, never a wildcard or both modes.
        headers = dict(HEADERS)
        headers['Content-Security-Policy'] = headers['Content-Security-Policy'].replace(
            "form-action 'self'", "form-action 'self' https://" + self.paypal_host)
        return headers

    async def checkout(self, request):
        if request.method == 'GET':
            nonce = secrets.token_hex(20)
            headers = self._checkout_headers()
            headers['Content-Security-Policy'] += "; script-src 'nonce-" + nonce + "'"
            return HTMLResponse('''<!doctype html><html lang="sv"><meta charset="utf-8">
<title>ARN avtalsinformation</title><p>Hämtar ditt avtalsunderlag…</p>
<form id="entry" method="post"><input name="stage" value="show" type="hidden">
<input id="cap" name="token" type="hidden"></form><script nonce="''' + nonce + '''">
const t=location.hash.slice(1);history.replaceState(null,'',location.pathname);
if(/^[a-f0-9]{64}$/.test(t)){document.getElementById('cap').value=t;document.getElementById('entry').submit();}
</script><noscript>JavaScript behövs för denna skyddade avtalslänk. Kontakta arn-support@qysley.se.</noscript></html>''', headers=headers)
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
            raw = parse_qs(body.decode(), keep_blank_values=True, max_num_fields=5)
            if any(len(v) != 1 for v in raw.values()):
                raise ValueError()
            data = {k: v[0] for k, v in raw.items()}
            token = data.get('token', '')
            with self.connection() as conn:
                row = self._session(conn, token)
                if row is None:
                    return text_response('Avtalslänken är inte tillgänglig.', 404)
                if data.get('stage') == 'show' and set(data) == {'stage', 'token'}:
                    price = '59 SEK per månad' if row['plan'] == 'monthly' else '590 SEK per år'
                    response = HTMLResponse('<!doctype html><html lang="sv"><meta charset="utf-8">'
                        '<title>ARN avtalsinformation</title><h1>' + price + '</h1><pre>'
                        + html.escape(row['terms']) + '</pre><h2>Integritetsinformation</h2><pre>'
                        + html.escape(row['privacy']) + '</pre><pre>' + html.escape(row['instructions'])
                        + '</pre><p><a href="' + html.escape(self.base + '/consumer/withdrawal', quote=True)
                        + '">Ångra avtalet här</a></p><form method="post">'
                        + '<input type="hidden" name="stage" value="continue">'
                        + '<input type="hidden" name="token" value="' + token + '">'
                        + '<input type="hidden" name="csrf" value="' + self.mac('checkout:' + token) + '">'
                        + '<label><input type="checkbox" name="consent" value="yes" required>'
                        + 'Jag har tagit del av avtalsinformationen och väljer nedladdad textfil '
                        + 'för avtalsbekräftelsen.</label><button>Fortsätt till PayPal — ' + price
                        + '</button></form></html>', headers=self._checkout_headers())
                    response.set_cookie('arn_checkout', token, max_age=86400, secure=True,
                                        httponly=True, samesite='strict', path=self.cookie_path)
                    return response
                if (set(data) != {'stage', 'token', 'csrf', 'consent'} or data['stage'] != 'continue'
                        or data['consent'] != 'yes' or request.cookies.get('arn_checkout') != token
                        or not secrets.compare_digest(data['csrf'], self.mac('checkout:' + token))):
                    return text_response('Bekräftelse av avtalsinformationen krävs.', 400)
                # Resolve only the existing, server-registered intent for this account.
                destination = self._paypal_url(self.lookup_approval(row['user_id'], row['subscription_id']))
                conn.execute('UPDATE checkout_sessions SET consent_at=COALESCE(consent_at,?) WHERE cap_hash=?',
                             (datetime.fromtimestamp(self.clock(), timezone.utc).isoformat(), row['cap_hash']))
            return Response(status_code=303, headers={**self._checkout_headers(), 'Location': destination})
        except Exception:
            return technical_error('consumer_checkout')

    def record_approval(self, subscription_id, details, result):
        """Only called with the existing verified server PayPal response, never form input."""
        if (result not in {'verified', 'pending'} or details.get('id') != subscription_id
                or details.get('status') not in {'APPROVED', 'ACTIVE'}):
            return False
        with self.connection() as conn:
            self._schema(conn)
            rows = conn.execute('SELECT * FROM checkout_sessions WHERE subscription_id=? '
                                'AND user_id=? AND consent_at IS NOT NULL',
                                (subscription_id, details.get('custom_id'))).fetchall()
            saved = False
            for row in rows:
                if details.get('plan_id') != self.plan_ids[row['plan']]:
                    continue
                stamp = datetime.fromtimestamp(self.clock(), timezone.utc).isoformat()
                price = '59 SEK/månad' if row['plan'] == 'monthly' else '590 SEK/år'
                confirmation = ('Avtalsbekräftelse — ARN Konsumenttvist MCP\n'
                                f'Abonnemang: {subscription_id}\nPris: {price}\n'
                                f'PayPal-godkännandet verifierades: {stamp}\n'
                                'Denna kontrolltid är inte ett påstående om exakt tid för kundens godkännande.\n'
                                + ('Betald åtkomst verifierad.\n' if result == 'verified'
                                   else 'Betalning är ännu inte verifierad; betald åtkomst bekräftas inte.\n')
                                + '\nVillkor, oföränderlig kopia:\n' + row['terms']
                                + '\nIntegritetsinformation:\n' + row['privacy']
                                + '\nÅngerinformation och blankett:\n' + row['instructions'])
                conn.execute('UPDATE checkout_sessions SET confirmation=COALESCE(confirmation,?) WHERE cap_hash=?',
                             (confirmation, row['cap_hash']))
                saved = True
            return saved

    async def confirmation(self, request):
        if not self.admit():
            return technical_error('consumer_admission')
        try:
            with self.connection() as conn:
                row = self._session(conn, request.cookies.get('arn_checkout', ''))
                if row is None or not row['confirmation']:
                    return text_response('Bekräftelsen är inte tillgänglig.', 404)
                response = text_response(row['confirmation'])
                response.headers['Content-Disposition'] = 'attachment; filename="arn-avtalsbekraftelse.txt"'
                return response
        except Exception:
            return technical_error('consumer_confirmation')

    def delivery_response(self, title, message, status):
        """Customer selected file delivery before approval; initiate it, retain retry link."""
        nonce = secrets.token_hex(20)
        target = self.base + '/consumer/confirmation'
        headers = dict(HEADERS)
        headers['Content-Security-Policy'] += "; script-src 'nonce-" + nonce + "'"
        script_target = json.dumps(target).replace('<', '\\u003c')
        return HTMLResponse('<!doctype html><html lang="sv"><meta charset="utf-8"><title>'
                            + html.escape(title) + '</title><h1>' + html.escape(title) + '</h1><p>'
                            + html.escape(message) + '</p><p><a href="' + html.escape(target, quote=True)
                            + '">Hämta din avtalsbekräftelse som textfil</a></p>'
                            + '<script nonce="' + nonce + '">window.location.assign(' + script_target
                            + ');</script><noscript>Hämta bekräftelsen med länken ovan.</noscript></html>',
                            status_code=status, headers=headers)

    def operator_payload(self, serialized):
        data = json.loads(serialized)
        message = EmailMessage(policy=policy.SMTPUTF8)
        message['From'] = data['email'] or 'arn-support@qysley.se'
        message['To'] = 'arn-support@qysley.se'
        message['Subject'] = 'Ångerbegäran — ARN Konsumenttvist MCP'
        message.set_content('Obekräftad identitet/kontokoppling. Ingen automatisk betalningsåtgärd.\n'
                            + '\n'.join(k + ': ' + str(v) for k, v in data.items()))
        return json.dumps({'envelope_from': data['email'], 'envelope_to': 'arn-support@qysley.se',
                           'raw_hex': message.as_bytes().hex()}).encode()


def register_integrated_routes(server, flow):
    register_consumer_routes(server, flow)
    server.custom_route('/consumer/checkout', methods=['GET', 'POST'], include_in_schema=False)(flow.checkout)
    server.custom_route('/consumer/confirmation', methods=['GET'], include_in_schema=False)(flow.confirmation)


def read_consumer_subject_data(database, *, user_id, verified_subject):
    """Private operator selection after separate identity verification, no delivery.

    Form submissions are unverified and cannot be attributed by email alone.
    """
    if (not isinstance(user_id, str) or not user_id or user_id != user_id.strip()
            or len(user_id) > 512 or '\0' in user_id or verified_subject != user_id):
        raise PermissionError('Verified subject required')
    path = Path(database)
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('Consumer data source unavailable')
    try:
        with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA query_only=ON')
            conn.execute('BEGIN')
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
            if tables - {'checkout_sessions', 'withdrawal_requests'}:
                raise ValueError()
            rows = [] if 'checkout_sessions' not in tables else [dict(r) for r in conn.execute(
                'SELECT user_id,subscription_id,plan,created,terms,privacy,instructions,consent_at,confirmation '
                'FROM checkout_sessions WHERE user_id=? ORDER BY created', (user_id,))]
        return {'subject': user_id, 'checkout_sessions': rows, 'complete': False,
                'unverified_withdrawals_require_manual_linkage': True, 'delivery_verified': False}
    except Exception:
        raise RuntimeError('Consumer data selection unavailable') from None
