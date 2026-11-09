"""Focused synthetic checks for non-operator disclosure admission."""
import ast,hashlib,json,os
from pathlib import Path
import tempfile,unittest
from unittest.mock import Mock,patch
from disclosure_policy import DisclosureBlocked,DisclosurePolicy,policy_from_environment,revision_for,subject_reference


class DisclosureTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.path=self.root/'policy.json';self.uid=os.getuid() if hasattr(os,'getuid') else 1000
        self.policy=DisclosurePolicy(self.path,owner_uid=self.uid)
    def tearDown(self):self.tmp.cleanup()
    def write(self,subjects=()):
        blocked=sorted(subject_reference(s) for s in subjects);digest='a'*64
        value={'version':1,'source_digest':digest,'blocked_subjects':blocked,'revision':revision_for(digest,blocked)}
        self.path.write_text(json.dumps(value));self.path.chmod(0o600);return value
    def test_fresh_policy_reloads_and_other_account_is_unchanged(self):
        self.write();self.assertTrue(self.policy.require_disclosure('A')['permitted'])
        self.write(['A'])
        with self.assertRaises(DisclosureBlocked) as e:self.policy.require_disclosure('A')
        self.assertEqual(e.exception.reason,'restricted');self.assertTrue(self.policy.require_disclosure('B')['permitted'])
    def test_missing_corrupt_or_stale_revision_fails_closed(self):
        with self.assertRaises(DisclosureBlocked):self.policy.require_disclosure('A')
        value=self.write();value['blocked_subjects']=[subject_reference('A')]
        self.path.write_text(json.dumps(value))
        with self.assertRaises(DisclosureBlocked) as e:self.policy.require_disclosure('B')
        self.assertEqual(e.exception.reason,'unavailable')
        self.path.write_text('{')
        with self.assertRaises(DisclosureBlocked):self.policy.require_disclosure('A')
    def test_projection_contains_no_plain_subject_or_mail_content(self):
        self.write(['SYNTHETIC-ACCOUNT-PRIVATE'])
        raw=self.path.read_text();self.assertNotIn('SYNTHETIC-ACCOUNT-PRIVATE',raw)
        self.assertEqual(set(json.loads(raw)),{'version','source_digest','blocked_subjects','revision'})
    def test_disabled_legacy_and_required_activation_are_distinct(self):
        with patch.dict(os.environ,{},clear=True):
            self.assertIsNone(policy_from_environment())
            with self.assertRaises(DisclosureBlocked):policy_from_environment(required=True)
        with self.assertRaises(DisclosureBlocked):DisclosurePolicy('relative.json')
    def test_wrong_owner_and_world_readable_policy_are_rejected_on_linux(self):
        self.write()
        if os.name=='posix':
            with self.assertRaises(DisclosureBlocked):DisclosurePolicy(self.path,owner_uid=self.uid+1).require_disclosure('A')
            self.path.chmod(0o644)
            with self.assertRaises(DisclosureBlocked):self.policy.require_disclosure('A')
        else:
            # Windows ACLs are an explicit deployment gate, not inferred from chmod.
            self.assertTrue(self.policy.require_disclosure('A')['permitted'])
    def test_duplicates_or_unknown_fields_are_not_accepted(self):
        value=self.write(['A']);value['blocked_subjects']*=2
        self.path.write_text(json.dumps(value))
        with self.assertRaises(DisclosureBlocked):self.policy.require_disclosure('B')
        value=self.write();value['allow_all']=True;self.path.write_text(json.dumps(value))
        with self.assertRaises(DisclosureBlocked):self.policy.require_disclosure('B')
    def test_actual_consume_helper_blocks_before_quota_and_upstream_work(self):
        root=Path(__file__).resolve().parents[1]
        source=root/'consumer-integration/arn_mcp.py'
        if not source.exists():source=root/'arn_mcp.py'  # public CI layout
        tree=ast.parse(source.read_text(encoding='utf-8'))
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='consume_for_tool')
        manager=Mock();manager.consume.return_value={'allowed':True,'paid':False}
        scope={'license_manager':manager,'CONSUMER_FLOW':None,'DISCLOSURE_POLICY':self.policy,
               'DisclosureBlocked':DisclosureBlocked,'safe_exception':lambda *a:RuntimeError(a[1])}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual disclosure admission>','exec'),scope)
        self.write(['A'])
        with self.assertRaisesRegex(RuntimeError,'processing_restricted'):scope['consume_for_tool']('A')
        manager.consume.assert_not_called()
        self.assertTrue(scope['consume_for_tool']('B')['allowed']);manager.consume.assert_called_once_with('B')
    def test_payment_and_webhook_functions_remain_unchanged(self):
        root=Path(__file__).resolve().parents[1];source=root/'consumer-integration/arn_mcp.py'
        if not source.exists():source=root/'arn_mcp.py'
        tree=ast.parse(source.read_text(encoding='utf-8'))
        expected={'record_verified_subscription':'3748e9ea2359eba6363bd4f968982ee6f1c86244d1ea631451677d2b30ddd7fe',
                  'verified_payment_period':'35202714c88ee6cd3ce3376d82aae0d8aa869944dab029c93f799e078813aed2',
                  'paypal_webhook':'d46fc400060393cb3b911a1a78e17c60c47d2cb08786bc4537e8e41342deb2df'}
        for name,digest in expected.items():
            node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
            self.assertEqual(hashlib.sha256(ast.dump(node).encode()).hexdigest(),digest)

if __name__=='__main__':unittest.main()
