import ast
from unittest.mock import Mock
import pytest
from conftest import ROOT,TOOLS,load_paypal
from test_tool_response_boundaries import ARGS
from mcp.server.mcpserver.exceptions import ToolError

@pytest.mark.parametrize('name',sorted(TOOLS))
def test_authenticated_tool_records_one_activity(tools,name):
    scope,client,manager,events=tools
    scope[name](**ARGS[name])
    assert manager.activity==['synthetic-user']

@pytest.mark.parametrize('name',sorted(TOOLS))
def test_quota_denial_still_records_activity(tools,name):
    scope,client,manager,events=tools;manager.allowed=False
    assert scope[name](**ARGS[name])['error']=='payment_required'
    assert manager.activity==['synthetic-user'];assert events==['consume']

@pytest.mark.parametrize('name',sorted(TOOLS))
def test_invalid_auth_does_not_record_activity(tools,name):
    scope,client,manager,events=tools
    scope['get_authenticated_user_id']=Mock(side_effect=ValueError('synthetic invalid identity'))
    with pytest.raises(ToolError):scope[name](**ARGS[name])
    assert manager.activity==[] and events==[]

@pytest.mark.parametrize('name',sorted(TOOLS))
def test_activity_write_failure_prevents_untracked_use(tools,name):
    scope,client,manager,events=tools;manager.record_user_activity=Mock(side_effect=RuntimeError('synthetic backend outage'))
    with pytest.raises(ToolError):scope[name](**ARGS[name])
    assert events==[]

@pytest.mark.parametrize('name',['arn_create_subscription','arn_cancel_subscription'])
def test_payment_activity_is_before_lock_admission(name):
    scope=load_paypal();scope['payment_lock']=Mock(side_effect=scope['PaymentBusy']('synthetic busy'))
    with pytest.raises(ToolError):scope[name]()
    scope['license_manager'].record_user_activity.assert_called_once_with('synthetic-user')
    scope['requests'].post.assert_not_called()

def test_admin_callbacks_and_transport_have_no_activity_calls():
    tree=ast.parse((ROOT/'arn_mcp.py').read_text(encoding='utf-8'))
    called=[]
    for f in tree.body:
        if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)) and any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='record_user_activity' for n in ast.walk(f)):
            called.append(f.name)
    assert set(called)==set(TOOLS)|{'arn_create_subscription','arn_cancel_subscription'}

def test_adapter_requires_positive_status():
    from arn_license import LicenseManager
    manager=object.__new__(LicenseManager);manager._request=Mock(return_value={'ok':True})
    manager.record_user_activity('synthetic-user')
    manager._request.assert_called_once_with('record_user_activity',user_id='synthetic-user')
    manager._request.return_value={'ok':'true'}
    with pytest.raises(RuntimeError):manager.record_user_activity('synthetic-user')
