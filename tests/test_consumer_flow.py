import ast
import asyncio
from contextlib import nullcontext
import hashlib
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch
import unittest
import html

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs7
from mcp.server.mcpserver import MCPServer
from starlette.requests import Request
from starlette.responses import HTMLResponse

from consumer_flow import ConsumerFlow, register_integrated_routes, read_consumer_subject_data
from consumer_runtime import configure_consumer
import test_consumer_handlers as base_tests


class FlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_tests.ConsumerTests.setUpClass.__func__(cls)

    def setUp(self):
        base_tests.ConsumerTests.setUp(self)
        self.lookups = []
        def lookup(user, sub):
            self.lookups.append((user, sub))
            return 'https://www.sandbox.paypal.com/approval?synthetic=1'
        self.handlers = ConsumerFlow(**self.settings, public_base_url='https://synthetic.invalid',
                                     paypal_host='www.sandbox.paypal.com',
                                     plan_ids={'monthly': 'SYNTH-MONTH', 'yearly': 'SYNTH-YEAR'},
                                     lookup_approval=lookup, withdrawal_instructions='IMMUTABLE-WITHDRAWAL-FORM')
        self.server = MCPServer(name='synthetic-integrated-r7', version='test-only')
        register_integrated_routes(self.server, self.handlers)
        self.app = self.server.streamable_http_app()

    tearDown = base_tests.ConsumerTests.tearDown
    run_http = base_tests.ConsumerTests.run_http
    form = base_tests.ConsumerTests.form
    post = base_tests.ConsumerTests.post

    def offer(self, user='A', sub='SYNTH-SUB-A'):
        return self.handlers.wrap_approval(user, 'monthly', sub,
                                           'https://www.sandbox.paypal.com/approval?synthetic=1').split('#')[1]

    async def show(self, client, token):
        return await client.post('/consumer/checkout', data={'stage': 'show', 'token': token},
                                 headers={'Origin': 'https://synthetic.invalid'})

    async def accept(self, client, token):
        return await client.post('/consumer/checkout', headers={'Origin': 'https://synthetic.invalid'},
                                 data={'stage': 'continue', 'token': token, 'consent': 'yes',
                                       'csrf': self.handlers.mac('checkout:' + token)})

    def details(self, user='A', sub='SYNTH-SUB-A'):
        return {'id': sub, 'custom_id': user, 'plan_id': 'SYNTH-MONTH', 'status': 'ACTIVE'}

    def test_information_must_be_shown_before_redirect(self):
        token = self.offer()
        async def run(client):
            self.assertEqual((await self.accept(client, token)).status_code, 400)
            page = await self.show(client, token)
            self.assertIn('SYNTHETIC-TERMS', page.text)
            self.assertIn('IMMUTABLE-WITHDRAWAL-FORM', page.text)
            self.assertNotIn('paypal.com/approval', page.text)
            self.assertEqual(self.lookups, [])
            response = await self.accept(client, token)
            self.assertEqual(response.status_code, 303)
            self.assertTrue(response.headers['location'].startswith('https://www.sandbox.paypal.com/'))
        self.run_http(run)

    def test_wrong_origin_and_provider_destination_rejected(self):
        with self.assertRaises(ValueError):
            self.handlers.wrap_approval('A', 'monthly', 'SUB', 'https://attacker.invalid/')
        with self.assertRaises(ValueError):
            self.handlers.wrap_approval('A', 'monthly', 'SUB', 'https://www.paypal.com/approval')
        token = self.offer()
        async def run(client):
            response = await client.post('/consumer/checkout', data={'stage': 'show', 'token': token},
                                         headers={'Origin': 'https://other.invalid'})
            self.assertEqual(response.status_code, 403)
        self.run_http(run)

    def test_browser_headers_keep_origin_check_and_exact_provider_policy(self):
        token = self.offer()
        async def run(client):
            page = await self.show(client, token)
            self.assertEqual(page.headers['referrer-policy'], 'same-origin')
            policy = page.headers['content-security-policy']
            self.assertIn("form-action 'self' https://www.sandbox.paypal.com;", policy)
            self.assertNotIn('https://www.paypal.com', policy)
            self.assertNotIn('*', policy)
            for origin in ('null', 'https://untrusted.invalid', ''):
                response = await client.post('/consumer/checkout',
                    data={'stage':'show','token':token}, headers={'Origin':origin})
                self.assertEqual(response.status_code, 403)
            withdrawal = await client.get('/consumer/withdrawal')
            self.assertIn("form-action 'self';", withdrawal.headers['content-security-policy'])
            self.assertNotIn('paypal.com', withdrawal.headers['content-security-policy'])
            data = await self.form(client)
            for origin in ('null', 'https://untrusted.invalid', ''):
                self.assertEqual((await self.post(client, data, origin)).status_code, 403)
        self.run_http(run)

    def test_confirmation_download_is_bound_to_capability(self):
        token = self.offer()
        async def run(client):
            await self.show(client, token)
            await self.accept(client, token)
            self.assertTrue(self.handlers.record_approval('SYNTH-SUB-A', self.details(), 'verified'))
            response = await client.get('/consumer/confirmation')
            self.assertEqual(response.status_code, 200)
            self.assertIn('attachment;', response.headers['content-disposition'])
            self.assertIn('SYNTHETIC-TERMS', response.text)
            self.assertIn('SYNTHETIC-PRIVACY', response.text)
            self.assertIn('IMMUTABLE-WITHDRAWAL-FORM', response.text)
            self.assertIn('Betald åtkomst verifierad', response.text)
            client.cookies.clear()
            denied = await client.get('/consumer/confirmation?subscription_id=SYNTH-SUB-A')
            self.assertEqual(denied.status_code, 404)
        self.run_http(run)

    def test_a_cannot_download_b_confirmation(self):
        a = self.offer()
        b = self.offer('B', 'SYNTH-SUB-B')
        async def run(client):
            await self.show(client, b)
            await self.accept(client, b)
            self.assertTrue(self.handlers.record_approval('SYNTH-SUB-B', self.details('B', 'SYNTH-SUB-B'), 'verified'))
            await self.show(client, a)
            denied = await client.get('/consumer/confirmation?subscription_id=SYNTH-SUB-B')
            self.assertEqual(denied.status_code, 404)
            self.assertNotIn('SYNTH-SUB-B', denied.text)
        self.run_http(run)

    def test_operator_subject_selection_excludes_other_account_and_tokens(self):
        self.offer('A', 'SYNTH-SUB-A')
        self.offer('B', 'SYNTH-SUB-B')
        result = read_consumer_subject_data(self.db, user_id='A', verified_subject='A')
        self.assertEqual(len(result['checkout_sessions']), 1)
        raw = json.dumps(result)
        self.assertNotIn('SYNTH-SUB-B', raw)
        self.assertNotIn('cap_hash', raw)
        self.assertFalse(result['complete'])
        with self.assertRaises(PermissionError):
            read_consumer_subject_data(self.db, user_id='A', verified_subject='B')

    def test_snapshot_and_pending_payment_not_rewritten(self):
        token = self.offer()
        self.handlers.terms = 'LATER-TERMS'
        async def run(client):
            self.assertNotIn('LATER-TERMS', (await self.show(client, token)).text)
            await self.accept(client, token)
            self.assertTrue(self.handlers.record_approval('SYNTH-SUB-A', self.details(), 'pending'))
            first = await client.get('/consumer/confirmation')
            self.assertIn('Betalning är ännu inte verifierad', first.text)
            self.handlers.record_approval('SYNTH-SUB-A', self.details(), 'verified')
            self.assertEqual(first.content, (await client.get('/consumer/confirmation')).content)
        self.run_http(run)

    def test_unverified_or_wrong_account_plan_never_confirms(self):
        token = self.offer()
        async def run(client):
            await self.show(client, token)
            await self.accept(client, token)
            for details in [self.details('B'), self.details() | {'plan_id': 'OTHER'},
                            self.details() | {'status': 'APPROVAL_PENDING'}]:
                self.assertFalse(self.handlers.record_approval('SYNTH-SUB-A', details, 'pending'))
            self.assertEqual((await client.get('/consumer/confirmation')).status_code, 404)
        self.run_http(run)

    def test_encrypted_case_reuses_existing_mail_record_format(self):
        import sqlite3
        from contextlib import closing
        async def run(client):
            self.assertEqual((await self.post(client, await self.form(client))).status_code, 200)
        self.run_http(run)
        with closing(sqlite3.connect(self.db)) as conn:
            cipher = conn.execute('SELECT ciphertext FROM withdrawal_requests').fetchone()[0]
        record = json.loads(pkcs7.pkcs7_decrypt_der(cipher, self.cert, self.key, []))
        self.assertEqual(record['envelope_to'], 'arn-support@qysley.se')
        self.assertIn(b'SYNTHETIC PERSON A', bytes.fromhex(record['raw_hex']))

    def test_actual_mcp_source_wraps_and_blocks_unconfigured_creation(self):
        source = Path(__file__).resolve().parent.parent/'arn_mcp.py'
        tree = ast.parse(source.read_text(encoding='utf-8'))
        nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in
                 {'create_subscription_locked', 'subscription_approval_response'}]
        for node in nodes:
            node.decorator_list = []
        license = Mock()
        license.get_active_subscription.return_value = None
        scope = dict(CONSUMER_FLOW=None, get_authenticated_user_id=lambda: 'A', license_manager=license,
                     PAYPAL_MONTHLY_PLAN_ID='SYNTH-MONTH', PAYPAL_YEARLY_PLAN_ID='SYNTH-YEAR',
                     PAYPAL_MONTHLY_AMOUNT=59, PAYPAL_YEARLY_AMOUNT=590)
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual-local-mcp>', 'exec'), scope)
        with self.assertRaises(RuntimeError):
            scope['create_subscription_locked']('monthly')
        license.ensure_user.assert_not_called()
        scope['CONSUMER_FLOW'] = self.handlers
        result = scope['subscription_approval_response']('monthly', 59, 'SYNTH-SUB-A',
                                                        'https://www.sandbox.paypal.com/approval?synthetic=1')
        self.assertTrue(result['approval_url'].startswith('https://synthetic.invalid/consumer/checkout#'))
        self.assertNotIn('paypal.com', result['approval_url'])

    def test_actual_success_handler_uses_single_existing_provider_read(self):
        source = Path(__file__).resolve().parent.parent/'arn_mcp.py'
        node = next(n for n in ast.parse(source.read_text(encoding='utf-8')).body
                    if isinstance(n, ast.AsyncFunctionDef) and n.name == 'paypal_success')
        node.decorator_list = []
        provider = Mock(return_value=self.details())
        scope = dict(CONSUMER_FLOW=self.handlers, paypal_subscription_details=provider,
                     record_verified_subscription=lambda *a: 'verified', payment_lock=lambda *a: nullcontext(),
                     LICENSE_DB='synthetic', failure=Mock(), html=html, ARN_PUBLIC_URL='https://synthetic.invalid',
                     HTMLResponse=HTMLResponse, Request=Request)
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<actual-success-handler>', 'exec'), scope)
        token = self.offer()
        async def run(client):
            await self.show(client, token)
            await self.accept(client, token)
            req = Request({'type': 'http', 'method': 'GET', 'path': '/paypal/success',
                           'query_string': b'subscription_id=SYNTH-SUB-A', 'headers': []})
            response = await scope['paypal_success'](req)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'/consumer/confirmation', response.body)
            self.assertEqual((await client.get('/consumer/confirmation')).status_code, 200)
        self.run_http(run)
        provider.assert_called_once()

    def test_actual_webhook_records_confirmation_without_browser_return(self):
        source = Path(__file__).resolve().parent.parent/'arn_mcp.py'
        node = next(n for n in ast.parse(source.read_text(encoding='utf-8')).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'process_paypal_event')
        node.decorator_list = []
        provider = Mock(return_value=self.details())
        payment = Mock(return_value='verified')
        scope = dict(CONSUMER_FLOW=self.handlers, paypal_subscription_details=provider,
                     record_verified_subscription=payment,
                     get_subscription_id_from_resource=lambda resource: resource['id'])
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<actual-webhook>', 'exec'), scope)
        token = self.offer()
        async def run(client):
            await self.show(client, token)
            await self.accept(client, token)
            # No /paypal/success call, no provider navigation or extra API call.
            event={'id':'SYNTH-EVENT','event_type':'BILLING.SUBSCRIPTION.ACTIVATED',
                   'resource':{'id':'SYNTH-SUB-A'}}
            scope['process_paypal_event'](event)
            first=await client.get('/consumer/confirmation')
            self.assertEqual(first.status_code,200)
            scope['process_paypal_event'](event)
            self.assertEqual(first.content,(await client.get('/consumer/confirmation')).content)
        self.run_http(run)
        self.assertEqual(provider.call_count,2)
        self.assertEqual(payment.call_count,2)

    def test_consumer_webhook_failure_stays_retriable_and_payment_logic_unchanged(self):
        source = Path(__file__).resolve().parent.parent/'arn_mcp.py'
        tree=ast.parse(source.read_text(encoding='utf-8'))
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='process_paypal_event')
        flow=Mock();flow.record_approval.side_effect=[RuntimeError('synthetic consumer outage'),True]
        payment=Mock(return_value='pending');provider=Mock(return_value=self.details())
        scope=dict(CONSUMER_FLOW=flow,paypal_subscription_details=provider,
                   record_verified_subscription=payment,get_subscription_id_from_resource=lambda r:r['id'])
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-webhook>','exec'),scope)
        event={'id':'SYNTH-EVENT','event_type':'BILLING.SUBSCRIPTION.ACTIVATED','resource':{'id':'SYNTH-SUB-A'}}
        with self.assertRaises(RuntimeError):scope['process_paypal_event'](event)
        scope['process_paypal_event'](event)
        self.assertEqual(flow.record_approval.call_count,2)
        # AST fingerprints from the frozen, previously verified R11 baseline.
        # Keep this portable: no private review path or fixture is needed in CI.
        fingerprints={
            'record_verified_subscription':'3748e9ea2359eba6363bd4f968982ee6f1c86244d1ea631451677d2b30ddd7fe',
            'verified_payment_period':'35202714c88ee6cd3ce3376d82aae0d8aa869944dab029c93f799e078813aed2',
            'paypal_webhook':'d46fc400060393cb3b911a1a78e17c60c47d2cb08786bc4537e8e41342deb2df'}
        for name,digest in fingerprints.items():
            a=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
            self.assertEqual(hashlib.sha256(ast.dump(a,include_attributes=False).encode()).hexdigest(),digest)

    def test_config_unapproved_or_missing_does_not_register(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(configure_consumer(self.server, license_database=self.db,
                                               base_url='https://synthetic.invalid', plan_ids={}))

    def test_approved_config_mounts_and_reads_existing_intent_without_write(self):
        import sqlite3
        from contextlib import closing
        folder = Path(self.tmp.name)
        license_db = folder/'synthetic-license.db'
        with closing(sqlite3.connect(license_db)) as conn, conn:
            conn.execute('CREATE TABLE paypal_creation_intents(user_id TEXT, subscription_id TEXT, state TEXT, approval_url TEXT)')
            conn.execute('INSERT INTO paypal_creation_intents VALUES (?,?,?,?)',
                         ('A', 'SYNTH-SUB-A', 'registered', 'https://www.sandbox.paypal.com/approval?synthetic=1'))
        before = license_db.read_bytes()
        config = {'publication_approved': True, 'certificate_sha256': self.settings['certificate_sha256'],
                  'receipt_directory': str(folder/'synthetic-receipts'), 'receipt_owner_uid': 100001}
        cert = folder/'recipient.pem'
        cert.write_bytes(self.cert.public_bytes(serialization.Encoding.PEM))
        secret = folder/'consumer-secret.bin'
        secret.write_bytes(self.settings['secret'])
        secret.chmod(0o600)
        config.update(certificate_file=str(cert), secret_file=str(secret))
        for key in ['terms', 'privacy', 'withdrawal']:
            file = folder/(key + '.txt')
            file.write_text('APPROVED-SYNTHETIC-' + key, encoding='utf-8')
            config[key + '_file'] = str(file)
            config[key + '_sha256'] = hashlib.sha256(file.read_bytes()).hexdigest()
        path = folder/'approved-config.json'
        path.write_text(json.dumps(config), encoding='utf-8')
        server = MCPServer(name='real-config-synthetic-test')
        with patch.dict(os.environ, {'ARN_CONSUMER_CONFIG': str(path)}), patch(
                'consumer_runtime.ConsumerFlow', side_effect=lambda **kw: ConsumerFlow(
                    clock=lambda: self.now.timestamp(), **kw)),patch('consumer_runtime.policy_from_environment',return_value=Mock()):
            flow = configure_consumer(server, license_database=license_db,
                                      base_url='https://synthetic.invalid',
                                      plan_ids=self.handlers.plan_ids, paypal_environment='sandbox')
        self.assertEqual(flow.lookup_approval('A', 'SYNTH-SUB-A'),
                         'https://www.sandbox.paypal.com/approval?synthetic=1')
        self.assertIsNone(flow.lookup_approval('B', 'SYNTH-SUB-A'))
        self.assertEqual(before, license_db.read_bytes())
        self.handlers, self.app = flow, server.streamable_http_app()
        token = self.offer()
        async def run(client):
            self.assertEqual((await self.show(client, token)).status_code, 200)
            self.assertEqual((await self.accept(client, token)).status_code, 303)
        self.run_http(run)
        config = Path(self.tmp.name, 'unapproved.json')
        config.write_text('{"publication_approved": false}', encoding='utf-8')
        with patch.dict(os.environ, {'ARN_CONSUMER_CONFIG': str(config)}):
            self.assertIsNone(configure_consumer(self.server, license_database=self.db,
                                               base_url='https://synthetic.invalid', plan_ids={}))


    def test_actual_full_module_with_active_consumer_routes_preserves_auth(self):
        import shutil
        import subprocess
        import sys
        folder = Path(self.tmp.name)
        source = Path(__file__).resolve().parent.parent
        full = folder/'full-app'
        full.mkdir()
        for f in source.glob('*.py'):
            shutil.copyfile(f, full/f.name)
        config = {'publication_approved': True, 'certificate_sha256': self.settings['certificate_sha256'],
                  'receipt_directory': str(folder/'synthetic-receipts'), 'receipt_owner_uid': 100001}
        cert = folder/'active-recipient.pem'
        cert.write_bytes(self.cert.public_bytes(serialization.Encoding.PEM))
        secret = folder/'active-secret.bin'
        secret.write_bytes(self.settings['secret'])
        secret.chmod(0o600)
        config.update(certificate_file=str(cert), secret_file=str(secret))
        for key in ['terms', 'privacy', 'withdrawal']:
            path = folder/('active-' + key + '.txt')
            path.write_text('SYNTHETIC-ACTIVE-' + key, encoding='utf-8')
            config[key + '_file'] = str(path)
            config[key + '_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        path = folder/'active-config.json'
        path.write_text(json.dumps(config), encoding='utf-8')
        shutil.copytree(source/'library',full/'library')
        from library_lifecycle import initialize
        control=initialize(full/'control/revocations.json',full/'trust/anchor.json',full/'control/readers.lock')
        startup_source = (source/'tests/test_startup.py').read_text(encoding='utf-8')
        code = next(n.value.value for n in ast.walk(ast.parse(startup_source))
                    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'code' for t in n.targets)
                    and isinstance(n.value, ast.Constant))
        marker = 'import httpx,requests,urllib.request,uvicorn'
        code = code.replace(marker, marker + '\nimport consumer_runtime\n'
                            'import disclosure_policy as dp,os\n'
                            'original_policy=dp.DisclosurePolicy\n'
                            'dp.DisclosurePolicy=lambda path:original_policy(path,owner_uid=os.getuid() if hasattr(os,"getuid") else 100001)\n'
                            'original_consumer=consumer_runtime.ConsumerFlow\n'
                            'consumer_runtime.ConsumerFlow=lambda **kw:original_consumer(clock=lambda:'
                            + repr(self.now.timestamp()) + ',**kw)\n')
        code = code.replace('    seen.append(True)',
                            "            r=await c.get('/consumer/withdrawal')\n"
                            "            assert r.status_code==200 and 'csrf' in r.text\n"
                            "    seen.append(True)")
        env = {k: os.environ[k] for k in ['SYSTEMROOT', 'WINDIR', 'PATH', 'TEMP', 'TMP', 'LANG'] if k in os.environ}
        from disclosure_policy import revision_for
        policy=folder/'synthetic-policy.json'
        policy.write_text(json.dumps({'version':1,'source_digest':'a'*64,'blocked_subjects':[],
                                      'revision':revision_for('a'*64,[])}));policy.chmod(0o600)
        env.update(PYTHONUTF8='1', ARN_CONSUMER_CONFIG=str(path),ARN_DISCLOSURE_POLICY=str(policy),
                   ARN_D1_API_URL='https://synthetic-backend.invalid', ARN_D1_API_SECRET='synthetic-only',
                   PAYPAL_ENV='sandbox', PAYPAL_CLIENT_ID='synthetic-client', PAYPAL_CLIENT_SECRET='synthetic-secret',
                   PAYPAL_WEBHOOK_ID='synthetic-hook', PAYPAL_MONTHLY_PLAN_ID='SYNTH-MONTH',
                   PAYPAL_YEARLY_PLAN_ID='SYNTH-YEAR', MCP_TRANSPORT='streamable-http')
        env.update(ARN_LIBRARY_APPROVALS_SHA256=hashlib.sha256((full/'library/approvals.json').read_bytes()).hexdigest(),
                   ARN_LIBRARY_REVOCATIONS=str(control.journal),ARN_LIBRARY_REVOCATION_ANCHOR=str(control.anchor),
                   ARN_LIBRARY_REVOCATION_LOCK=str(control.lock))
        result = subprocess.run([sys.executable, '-I', '-B', '-c', code, str(full)], cwd=full,
                                env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr[-1500:])
        self.assertIn('FULL_STARTUP_REAL_SDK_ASGI_SMOKE_PASS', result.stdout)

    def test_confirmation_download_respects_same_subject_disclosure_policy(self):
        from disclosure_policy import DisclosureBlocked
        policy=Mock();self.handlers.disclosure_policy=policy
        token=self.offer()
        async def run(client):
            await self.show(client,token);await self.accept(client,token)
            self.handlers.record_approval('SYNTH-SUB-A',self.details(),'verified')
            for reason,status in [('restricted',403),('unavailable',503)]:
                policy.require_disclosure.side_effect=DisclosureBlocked(reason)
                response=await client.get('/consumer/confirmation')
                self.assertEqual(response.status_code,status)
                self.assertNotIn('IMMUTABLE',response.text)
                self.assertNotIn('SYNTH-SUB-A',response.text)
                policy.require_disclosure.assert_called_with('A')
            policy.require_disclosure.side_effect=None
            self.assertEqual((await client.get('/consumer/confirmation')).status_code,200)
        self.run_http(run)

    def test_fragment_bootstrap_javascript_clears_url_before_post(self):
        import re
        import shutil
        import subprocess
        if not shutil.which('node'):
            self.skipTest('Existing Node needed for bootstrap VM test; no dependency installed')
        req = Request({'type': 'http', 'method': 'GET', 'path': '/consumer/checkout',
                       'query_string': b'', 'headers': []})
        response = asyncio.run(self.handlers.checkout(req))
        script = re.search(r'<script nonce="[^"]+">(.*?)</script>', response.body.decode(), re.S)[1]
        delivery = self.handlers.delivery_response('Verifierat', 'Syntetiskt', 200)
        delivery_script = re.search(r'<script nonce="[^"]+">(.*?)</script>', delivery.body.decode(), re.S)[1]
        harness = r'''const vm=require('node:vm');const script=JSON.parse(process.argv[1]);
for(const value of ['a'.repeat(64),'bad','']){
 const events=[],field={value:''};
 const context={location:{hash:'#'+value,pathname:'/consumer/checkout'},
 history:{replaceState:(a,b,path)=>events.push(['clear',path])},
 document:{getElementById:(id)=>id==='cap'?field:{submit:()=>events.push(['post',field.value])}}};
 vm.runInNewContext(script,context,{timeout:100});
 if(events[0][0]!=='clear'||events[0][1]!=='/consumer/checkout')throw Error('URL not cleared');
 if((events.length===2)!==(value.length===64))throw Error('Invalid fragment handling');
}
let delivered='';vm.runInNewContext(JSON.parse(process.argv[2]),{window:{location:{assign:u=>delivered=u}}},{timeout:100});
if(delivered!=='https://synthetic.invalid/consumer/confirmation')throw Error('Wrong file delivery URL');
console.log('BOOTSTRAP_3_CASES_PASS');'''
        result = subprocess.run(['node', '-e', harness, json.dumps(script), json.dumps(delivery_script)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertIn('BOOTSTRAP_3_CASES_PASS', result.stdout)


if __name__ == '__main__':
    unittest.main()
