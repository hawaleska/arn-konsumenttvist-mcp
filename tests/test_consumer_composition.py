"""Exact boundaries of the consumer overlay on the working summary assembly."""
import ast,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SIX={'arn_search','arn_get_decision','arn_search_and_read','arn_search_company','arn_search_company_and_read','arn_similar_cases'}
def functions(path):
 return {n.name:n for n in ast.parse(path.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
def test_only_previously_reviewed_consumer_hooks_change_existing_functions():
 before=functions(ROOT/'baseline/installed-main.py');after=functions(ROOT/'arn_mcp.py')
 changed={n for n in before if ast.dump(before[n])!=ast.dump(after[n])}
 assert changed==SIX|{'create_subscription_locked','subscription_approval_response','process_paypal_event','paypal_success'}
 assert set(after)-set(before)=={'consume_for_tool'}
 for name in SIX:
  expected=copy.deepcopy(before[name])
  for node in ast.walk(expected):
   if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='license_manager' and node.func.attr=='consume':
    node.func=ast.Name(id='consume_for_tool',ctx=ast.Load())
  actual=copy.deepcopy(after[name])
  for fn in (expected,actual):
   for dec in fn.decorator_list:
    if isinstance(dec,ast.Call) and isinstance(dec.func,ast.Attribute) and dec.func.attr=='tool':
     dec.keywords=[k for k in dec.keywords if k.arg!='description']
  if name=='arn_search':
   # Approved 1.0.5 delta: an optional cursor and page metadata only for the
   # reviewed-index client. Keep the quota/auth prefix and legacy arguments
   # locked to the verified baseline; pagination is separately contract-tested.
   assert [a.arg for a in actual.args.args]==[a.arg for a in expected.args.args]+['cursor']
   assert actual.args.defaults[-1].value==''
   expected.args=copy.deepcopy(actual.args)
   expected.args.args=expected.args.args[:-1]
   expected.args.defaults=expected.args.defaults[:-1]
   actual_prefix=copy.deepcopy(actual.body[:4])
   expected_prefix=copy.deepcopy(expected.body[:4])
   assert ast.dump(ast.Module(body=expected_prefix,type_ignores=[]))==ast.dump(ast.Module(body=actual_prefix,type_ignores=[]))
   assert any(isinstance(n,ast.If) and 'source_mode' in ast.dump(n.test) and 'cursor' in ast.dump(n) for n in actual.body)
   assert any(isinstance(n,ast.If) and 'source_mode' in ast.dump(n.test) and 'continuation_cost' in ast.dump(n) for n in actual.body)
  else:
   assert ast.dump(expected)==ast.dump(actual)
 for name in before:
  if name!='arn_search':
   assert ast.dump(before[name].args)==ast.dump(after[name].args)
def test_auth_payment_library_and_live_read_fix_preserved_byte_for_byte():
 baseline=json.loads((ROOT/'COMPOSITION.json').read_text())['production_baseline']
 for name in ['arn_auth.py','arn_client.py','arn_license.py','arn_paypal_store.py','arn_library_client.py','library_lifecycle.py']:
  assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==baseline[name]
def test_error_contract_only_adds_two_previously_approved_consumer_codes():
 baseline=ast.parse((ROOT/'baseline/installed-errors.py').read_bytes());after=ast.parse((ROOT/'arn_errors.py').read_bytes())
 def messages(tree):return next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MESSAGES' for t in n.targets))
 added=messages(after);pairs=[(k,v) for k,v in zip(added.keys,added.values) if k.value not in {'confirmation_pending','processing_restricted'}]
 added.keys=[k for k,v in pairs];added.values=[v for k,v in pairs]
 assert ast.dump(baseline)==ast.dump(after)
