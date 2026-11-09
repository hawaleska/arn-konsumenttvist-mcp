"""R8/R9 admission policy, with no network or real quota."""
from unittest.mock import Mock
import pytest
from conftest import ROOT, TOOLS, load_tools, Registry, Client, License
from test_tool_response_boundaries import ARGS
from mcp.server.mcpserver.exceptions import ToolError

@pytest.mark.parametrize('tool', sorted(TOOLS))
def test_backend_failure_prevents_all_upstream_calls(tools,tool):
    scope,client,license,events=tools
    license.consume=Mock(side_effect=RuntimeError('synthetic failure'))
    with pytest.raises(ToolError):scope[tool](**ARGS[tool])
    assert events==[]
    license.consume.assert_called_once_with('synthetic-user')

@pytest.mark.parametrize('tool',['arn_search','arn_search_company','arn_search_and_read','arn_search_company_and_read'])
def test_empty_result_is_one_admitted_attempt(tools,tool):
    scope,client,license,events=tools
    client.rows=[]
    result=scope[tool](**ARGS[tool])
    assert result['count']==0
    assert events==['consume','search']

@pytest.mark.parametrize('tool',['arn_search_and_read','arn_search_company_and_read'])
def test_multiple_and_failed_decision_reads_still_one_attempt(tools,tool):
    scope,client,license,events=tools
    client.rows*=3;client.failure=True
    result=scope[tool](**ARGS[tool])
    assert result['count']==3
    assert all(row['error']=='decision_unavailable' for row in result['decisions'])
    assert events.count('consume')==1

@pytest.mark.parametrize('value',[None,0,1,'true','false',{},[]])
def test_malformed_backend_admission_is_never_truthy_permission(value,monkeypatch):
    from arn_license import LicenseManager
    manager=object.__new__(LicenseManager)
    manager._request=Mock(return_value={'allowed':value})
    with pytest.raises(RuntimeError):manager.consume('synthetic-user')

def test_parallel_last_credit_blocks_data_for_losers():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Lock
    events=[];client=Client(events)
    class AtomicLicense:
        def __init__(self):self.remaining=1;self.lock=Lock()
        def record_user_activity(self,user):pass
        def consume(self,user):
            with self.lock:
                allowed=self.remaining>0
                if allowed:self.remaining-=1
                return {'allowed':allowed,'paid':False,'remaining':self.remaining}
    license=AtomicLicense();scope=load_tools(Registry(),client,license)
    with ThreadPoolExecutor(max_workers=12) as pool:
        results=list(pool.map(lambda _:scope['arn_search'](query='synthetic'),range(20)))
    assert sum('error' not in result for result in results)==1
    assert events==['search']
    assert sum(result.get('error')=='payment_required' for result in results)==19

@pytest.mark.parametrize('tool', sorted(TOOLS))
def test_upstream_failure_after_admission_counts_once(tools,tool):
    scope,client,license,events=tools
    method='get_decision' if tool=='arn_get_decision' else 'similar_cases' if tool=='arn_similar_cases' else 'search'
    setattr(client,method,Mock(side_effect=RuntimeError('synthetic upstream failure')))
    with pytest.raises(ToolError):scope[tool](**ARGS[tool])
    assert events==['consume']

@pytest.mark.parametrize('tool', sorted(TOOLS))
def test_paid_tool_waits_for_account_bound_confirmation_before_ARN_read(tools,tool):
    import types
    scope,client,license,events=tools
    license.consume=Mock(return_value={'allowed':True,'paid':True,'remaining':None})
    license.get_subscription=Mock()
    check=Mock(return_value=False)
    scope['CONSUMER_FLOW']=types.SimpleNamespace(paid_confirmation_ready=check)
    with pytest.raises(ToolError,match='Avtalsbekräftelsen'):
        scope[tool](**ARGS[tool])
    assert events==[]
    license.consume.assert_called_once_with('synthetic-user')
    check.assert_called_once_with('synthetic-user',license.get_subscription)

@pytest.mark.parametrize('tool', sorted(TOOLS))
def test_paid_tool_proceeds_after_confirmation_without_second_quota_operation(tools,tool):
    import types
    scope,client,license,events=tools
    license.consume=Mock(return_value={'allowed':True,'paid':True,'remaining':None})
    license.get_subscription=Mock()
    scope['CONSUMER_FLOW']=types.SimpleNamespace(paid_confirmation_ready=Mock(return_value=True))
    assert 'error' not in scope[tool](**ARGS[tool])
    license.consume.assert_called_once_with('synthetic-user')
    assert 'consume' not in events
    assert events
