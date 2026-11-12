import asyncio
from contextlib import closing
from datetime import datetime, timedelta, timezone
import hashlib
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import unittest

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.x509.oid import NameOID
from mcp.server.mcpserver import MCPServer

from consumer_handlers import ConsumerHandlers, contract_confirmation, register_consumer_routes


class ConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.now = datetime(2026, 11, 7, 12, tzinfo=timezone.utc)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'synthetic-r7-recipient')])
        cls.cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
                    .public_key(cls.key.public_key()).serial_number(x509.random_serial_number())
                    .not_valid_before(cls.now - timedelta(days=1))
                    .not_valid_after(cls.now + timedelta(days=1)).sign(cls.key, hashes.SHA256()))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='synthetic-consumer-', dir=Path(__file__).parent)
        self.db = Path(self.tmp.name, 'requests.db')
        self.settings = dict(approved=True, origin='https://synthetic.invalid', database=self.db,
                             certificate=self.cert,
                             certificate_sha256=hashlib.sha256(self.cert.public_bytes(serialization.Encoding.DER)).hexdigest(),
                             secret=b'synthetic-secret-' * 3, terms='SYNTHETIC-TERMS', privacy='SYNTHETIC-PRIVACY',
                             clock=lambda: self.now.timestamp())
        self.handlers = ConsumerHandlers(**self.settings)
        self.server = MCPServer(name='synthetic-r7-consumer', version='test-only')
        register_consumer_routes(self.server, self.handlers)
        self.app = self.server.streamable_http_app()

    def tearDown(self):
        self.tmp.cleanup()

    def run_http(self, action):
        async def run():
            async with self.app.router.lifespan_context(self.app):
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),
                                             base_url='https://synthetic.invalid') as client:
                    return await action(client)
        return asyncio.run(run())

    async def form(self, client):
        response = await client.get('/consumer/withdrawal')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Path=/consumer', response.headers['set-cookie'])
        self.assertIn('href="information"', response.text)
        return {'csrf': re.search('name="csrf" value="([^"]+)"', response.text)[1],
                'name': 'SYNTHETIC PERSON A', 'email': 'synthetic-a@example.invalid',
                'reference': 'SYNTHETIC-SUB-A', 'receipt_format': 'text', 'confirm': 'yes'}

    def post(self, client, data, origin='https://synthetic.invalid'):
        return client.post('/consumer/withdrawal', data=data, headers={'Origin': origin})

    def test_html_contact_details_are_not_transformed_and_csp_is_not_relaxed(self):
        async def action(client):
            for path in ['/consumer/information', '/consumer/withdrawal']:
                response=await client.get(path)
                self.assertEqual(response.status_code,200)
                self.assertEqual(response.headers['cache-control'],'no-store, no-transform')
                self.assertIn("default-src 'none'",response.headers['content-security-policy'])
                self.assertNotIn('script-src',response.headers['content-security-policy'])
            self.assertIn('arn-support@qysley.se',(await client.get('/consumer/withdrawal')).text)
        self.run_http(action)

    def test_real_sdk_route_receipt_and_encrypted_storage(self):
        async def action(client):
            data = await self.form(client)
            response = await self.post(client, data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['cache-control'], 'no-store, no-transform')
            self.assertIn('attachment', response.headers['content-disposition'])
            self.assertIn('Mottaget:', response.text)
            self.assertIn('SYNTHETIC-SUB-A', response.text)
            self.assertNotIn(data['email'], response.text)
        self.run_http(action)
        with closing(sqlite3.connect(self.db)) as conn:
            encrypted = conn.execute('SELECT ciphertext FROM withdrawal_requests').fetchone()[0]
        plain = pkcs7.pkcs7_decrypt_der(encrypted, self.cert, self.key, [])
        self.assertIn(b'SYNTHETIC PERSON A', plain)
        self.assertNotIn(b'SYNTHETIC PERSON A', self.db.read_bytes())
        self.assertNotIn(b'synthetic-a@example.invalid', self.db.read_bytes())

    def test_publication_and_certificate_gates(self):
        for changes in ({'approved': False}, {'secret': b'short'}, {'certificate_sha256': 'wrong'},
                        {'origin': 'http://synthetic.invalid'}):
            with self.subTest(changes=list(changes)), self.assertRaises(ValueError):
                ConsumerHandlers(**(self.settings | changes))

    def test_missing_cookie_or_wrong_origin_never_writes(self):
        async def action(client):
            data = await self.form(client)
            self.assertEqual((await self.post(client, data, 'https://other.invalid')).status_code, 403)
            client.cookies.clear()
            self.assertEqual((await self.post(client, data)).status_code, 400)
        self.run_http(action)
        self.assertFalse(self.db.exists())

    def test_expired_csrf(self):
        async def action(client):
            data = await self.form(client)
            self.handlers.clock = lambda: self.now.timestamp() + 901
            self.assertEqual((await self.post(client, data)).status_code, 400)
        self.run_http(action)

    def test_duplicate_is_same_receipt_changed_payload_rejected(self):
        async def action(client):
            data = await self.form(client)
            first = await self.post(client, data)
            self.assertEqual(first.content, (await self.post(client, data)).content)
            data['reference'] = 'SYNTHETIC-SUB-B'
            self.assertEqual((await self.post(client, data)).status_code, 409)
        self.run_http(action)
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM withdrawal_requests').fetchone()[0], 1)

    def test_oversized_form(self):
        async def action(client):
            data = await self.form(client)
            data['name'] = 'x' * 5000
            self.assertEqual((await self.post(client, data)).status_code, 413)
        self.run_http(action)

    def test_control_characters_or_secret_like_reference_rejected(self):
        async def action(client):
            data = await self.form(client)
            for field, value in [('name', 'A\nB'), ('reference', 'https://invalid/?token=CANARY')]:
                changed = data | {field: value}
                self.assertEqual((await self.post(client, changed)).status_code, 400)
        self.run_http(action)

    def test_download_format_must_be_selected(self):
        async def action(client):
            data = await self.form(client)
            data['receipt_format'] = ''
            self.assertEqual((await self.post(client, data)).status_code, 400)
            data.update(receipt_format='text', email='', reference='')
            self.assertEqual((await self.post(client, data)).status_code, 400)
            data['reference'] = 'SYNTHETIC-SUB-A'
            self.assertEqual((await self.post(client, data)).status_code, 200)
        self.run_http(action)

    def test_existing_other_database_refused_and_unchanged(self):
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute('CREATE TABLE protected_canary(value TEXT)')
            conn.execute("INSERT INTO protected_canary VALUES ('DO-NOT-CHANGE')")
        before = self.db.read_bytes()
        async def action(client):
            response = await self.post(client, await self.form(client))
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json()['error'], 'backend_unavailable')
            self.assertTrue(response.json()['reference_id'])
            self.assertNotIn('protected_canary', response.text)
        self.run_http(action)
        self.assertEqual(before, self.db.read_bytes())

    def test_rate_limit_is_bounded_without_ip_tracking(self):
        async def action(client):
            for _ in range(30):
                self.assertEqual((await self.post(client, {}, 'https://other.invalid')).status_code, 403)
            self.assertEqual((await self.post(client, {})).status_code, 503)
        self.run_http(action)

    def test_information_is_escaped_and_includes_withdrawal(self):
        self.handlers.terms = '<script>SYNTHETIC</script>'
        async def action(client):
            response = await client.get('/consumer/information')
            self.assertNotIn('<script>', response.text)
            self.assertIn('&lt;script&gt;', response.text)
            self.assertIn('Ångra avtalet här', response.text)
        self.run_http(action)

    def test_parallel_duplicate_has_one_record_and_stable_receipt(self):
        async def action(client):
            data = await self.form(client)
            a, b = await asyncio.gather(self.post(client, data), self.post(client, data))
            self.assertEqual(a.status_code, 200)
            self.assertEqual(a.content, b.content)
        self.run_http(action)
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM withdrawal_requests').fetchone()[0], 1)

    @unittest.skipUnless(os.name == 'posix', 'POSIX permissions checked on Linux')
    def test_unsafe_storage_directory_is_rejected(self):
        self.db.parent.chmod(0o755)
        async def action(client):
            response = await self.post(client, await self.form(client))
            self.assertEqual(response.status_code, 503)
        self.run_http(action)
        self.assertFalse(self.db.exists())

    def test_durable_confirmation_requires_approval_and_keeps_full_text(self):
        values = dict(approval_verified=True, plan='monthly', approved_at_utc=self.now.isoformat(),
                      payment_verified=False, terms='IMMUTABLE-TERMS', privacy='IMMUTABLE-PRIVACY')
        result = contract_confirmation(**values)
        self.assertIn('IMMUTABLE-TERMS', result)
        self.assertIn('Betalning är inte verifierad', result)
        self.assertIn('14 dagars full', result)
        with self.assertRaises(ValueError):
            contract_confirmation(**(values | {'approval_verified': False}))
        with self.assertRaises(ValueError):
            contract_confirmation(**(values | {'payment_verified': 1}))


if __name__ == '__main__':
    unittest.main()
