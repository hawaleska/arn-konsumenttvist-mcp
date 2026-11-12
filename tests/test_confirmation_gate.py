"""Synthetic contract/account isolation and paid-tool integration only."""
import ast
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import Mock

from consumer_confirmation_gate import (confirmation_reference,paid_confirmation_ready,
                                      publish_acceptance,receipt_accepted)


class ConfirmationGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.database=self.root/'synthetic.sqlite3'
        with closing(sqlite3.connect(self.database)) as c,c:
            c.execute('CREATE TABLE checkout_sessions(user_id TEXT,subscription_id TEXT,consent_at TEXT,confirmation TEXT)')
        self.lookup=Mock(return_value={'user_id':'A','paypal_subscription_id':'SUB-A'})
        self.accepted=set()
        self.folder=self.root/'receipts';self.folder.mkdir();self.folder.chmod(0o2750)
        self.uid=os.getuid() if hasattr(os,'getuid') else 1000
    def tearDown(self):self.tmp.cleanup()
    def row(self,user='A',sub='SUB-A',consent='yes',text='SYNTHETIC TERMS'):
        with closing(sqlite3.connect(self.database)) as c,c:
            c.execute('INSERT INTO checkout_sessions VALUES(?,?,?,?)',(user,sub,consent,text))
        return confirmation_reference(user,sub,text or '')
    def ready(self,user='A'):
        before=hashlib.sha256(self.database.read_bytes()).hexdigest()
        result=paid_confirmation_ready(self.database,user,self.lookup,lambda ref:ref in self.accepted)
        self.assertEqual(before,hashlib.sha256(self.database.read_bytes()).hexdigest())
        return result
    def test_legacy_user_and_empty_schema_unchanged(self):
        self.assertTrue(self.ready());self.lookup.assert_not_called()
        with closing(sqlite3.connect(self.database)) as c,c:c.execute('DROP TABLE checkout_sessions')
        self.assertTrue(self.ready());self.lookup.assert_not_called()
    def test_new_contract_waits_for_exact_acceptance(self):
        ref=self.row();self.assertFalse(self.ready())
        self.accepted.add(ref);self.assertTrue(self.ready())
    def test_other_user_or_contract_receipt_cannot_release_A(self):
        self.row();self.accepted.add(self.row('B','SUB-B'))
        self.accepted.add(confirmation_reference('A','OTHER','SYNTHETIC TERMS'))
        self.assertFalse(self.ready())
    def test_other_user_subscription_response_denied(self):
        self.accepted.add(self.row())
        self.lookup.return_value={'user_id':'B','paypal_subscription_id':'SUB-A'}
        self.assertFalse(self.ready())
    def test_prepared_or_missing_confirmation_does_not_release(self):
        self.row(text=None);self.assertFalse(self.ready())
        self.accepted.add(confirmation_reference('A','SUB-A',''))
        self.assertFalse(self.ready())
    def test_changed_or_conflicting_snapshot_does_not_reuse_receipt(self):
        self.accepted.add(self.row(text='OLD SNAPSHOT'))
        self.row(text='CHANGED SNAPSHOT');self.assertFalse(self.ready())
    def test_old_contract_not_blocked_by_different_new_offer(self):
        self.row(sub='NEW-OFFER',consent=None,text=None)
        self.lookup.return_value={'user_id':'A','paypal_subscription_id':'LEGACY'}
        self.assertTrue(self.ready())
    def test_backend_failure_and_missing_database_fail_closed(self):
        self.row();self.lookup.side_effect=RuntimeError('synthetic backend failure')
        self.assertFalse(self.ready())
        self.assertFalse(paid_confirmation_ready(self.root/'missing.db','A',self.lookup,lambda r:True))
        self.assertFalse((self.root/'missing.db').exists())
    def test_receipt_roundtrip_restart_and_no_personal_content(self):
        ref=self.row();self.assertFalse(receipt_accepted(self.folder,self.uid,ref))
        publish_acceptance(self.folder,self.uid,ref)
        first=(self.folder/(ref+'.json')).read_bytes()
        publish_acceptance(self.folder,self.uid,ref)
        self.assertEqual(first,(self.folder/(ref+'.json')).read_bytes())
        self.assertTrue(receipt_accepted(self.folder,self.uid,ref))
        self.assertEqual(set(json.loads(first)),{'version','reference','smtp_accepted'})
        for private in (b'SYNTHETIC TERMS',b'SUB-A',b'@'):self.assertNotIn(private,first)
    def test_corrupt_unknown_or_nonaccepted_receipts_fail_closed(self):
        ref=self.row();p=self.folder/(ref+'.json')
        for data in (b'not json',b'{}',b'x'*257,json.dumps({'version':1,'reference':ref,'smtp_accepted':False}).encode(),
                     json.dumps({'version':1,'reference':ref,'smtp_accepted':1}).encode()):
            p.write_bytes(data);p.chmod(0o640)
            self.assertFalse(receipt_accepted(self.folder,self.uid,ref))
        self.assertFalse(receipt_accepted(self.folder,self.uid,'../foreign'))
    def test_all_six_data_tools_use_consumer_gate_and_R11_functions_unchanged(self):
        root=Path(__file__).resolve().parents[1]
        current=ast.parse((root/'arn_mcp.py').read_text(encoding='utf-8'))
        old=ast.parse((root/'baseline/installed-main.py').read_text(encoding='utf-8'))
        functions={n.name:n for n in current.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
        baseline={n.name:n for n in old.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
        for name in ('arn_search','arn_get_decision','arn_search_and_read','arn_search_company','arn_search_company_and_read','arn_similar_cases'):
            calls=[n for n in ast.walk(functions[name]) if isinstance(n,ast.Call)]
            self.assertEqual(sum(isinstance(n.func,ast.Name) and n.func.id=='consume_for_tool' for n in calls),1)
            self.assertFalse(any(isinstance(n.func,ast.Attribute) and n.func.attr=='consume' for n in calls))
        for name in ('verified_payment_period','record_verified_subscription','paypal_webhook'):
            self.assertEqual(ast.dump(functions[name]),ast.dump(baseline[name]))
    def test_atomic_consume_preserved_free_admin_and_disabled_flow_unaffected(self):
        tree=ast.parse((Path(__file__).resolve().parents[1]/'arn_mcp.py').read_text(encoding='utf-8'))
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='consume_for_tool')
        manager=Mock();flow=Mock();flow.paid_confirmation_ready.return_value=False
        namespace={'license_manager':manager,'CONSUMER_FLOW':flow,
                   'safe_exception':lambda *a:RuntimeError('confirmation_pending')}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'<bounded actual tool gate>','exec'),namespace)
        manager.consume.return_value={'allowed':True,'paid':True}
        with self.assertRaisesRegex(RuntimeError,'confirmation_pending'):namespace['consume_for_tool']('A')
        flow.paid_confirmation_ready.assert_called_once_with('A',manager.get_subscription)
        manager.consume.assert_called_once_with('A')
        for result in ({'allowed':True,'paid':False},{'allowed':False,'paid':False}):
            flow.reset_mock();manager.consume.return_value=result
            self.assertIs(namespace['consume_for_tool']('A'),result);flow.paid_confirmation_ready.assert_not_called()
        for malformed in (1,'true',None,{}):
            manager.consume.return_value={'allowed':True,'paid':malformed}
            with self.assertRaises(RuntimeError):namespace['consume_for_tool']('A')
        manager.consume.return_value={'allowed':True,'paid':True};namespace['CONSUMER_FLOW']=None
        self.assertTrue(namespace['consume_for_tool']('LEGACY')['allowed'])
    def test_denied_data_tools_never_contact_ARN(self):
        tree=ast.parse((Path(__file__).resolve().parents[1]/'arn_mcp.py').read_text(encoding='utf-8'))
        names=('arn_search','arn_get_decision','arn_search_and_read','arn_search_company','arn_search_company_and_read','arn_similar_cases')
        client=Mock();manager=Mock()
        def blocked(user):raise RuntimeError('confirmation_pending')
        for fn in tree.body:
            if not isinstance(fn,ast.FunctionDef) or fn.name not in names:continue
            fn.decorator_list=[]
            ns={'get_authenticated_user_id':lambda:'A','license_manager':manager,
                'consume_for_tool':blocked,'client':client}
            exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual data tool>','exec'),ns)
            with self.assertRaisesRegex(RuntimeError,'confirmation_pending'):ns[fn.name]('SYNTHETIC INPUT')
        self.assertEqual(client.mock_calls,[])

if __name__=='__main__':unittest.main()
