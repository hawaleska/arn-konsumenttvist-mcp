import ast
import copy
import inspect
import json
from pathlib import Path

import pytest

from arn_public_responses import TOOLS
from conftest import PRIVATE,INTERNAL_URL,ROOT

ARGS={'arn_search':{'query':'test'},'arn_get_decision':{'case_number':'2026-00001'},
      'arn_search_and_read':{'query':'test'},'arn_search_company':{'company':'test'},
      'arn_search_company_and_read':{'company':'test'},'arn_similar_cases':{'problem':'test'}}


@pytest.mark.parametrize('tool',sorted(TOOLS))
def test_real_function_success_and_quota_order(tools,tool):
    scope,client,license,events=tools
    before=copy.deepcopy(client.rows)
    result=scope[tool](**ARGS[tool])
    assert PRIVATE not in json.dumps(result) and INTERNAL_URL not in json.dumps(result)
    assert client.rows==before
    expected={
        'arn_search':['consume','search'],
        'arn_get_decision':['consume','get_decision'],
        'arn_search_and_read':['consume','search','get_decision'],
        'arn_search_company':['consume','search'],
        'arn_search_company_and_read':['consume','search','get_decision'],
        'arn_similar_cases':['consume','similar_cases'],
    }
    assert [e[0] if type(e) is tuple else e for e in events]==expected[tool]
    if tool.endswith('and_read'):
        call=events[-1][1]
        assert call['file_id']==PRIVATE and call['xsessiontag']==PRIVATE


@pytest.mark.parametrize('tool',sorted(TOOLS))
def test_denied_admission_never_calls_upstream(tools,tool):
    scope,client,license,events=tools
    license.allowed=False
    result=scope[tool](**ARGS[tool])
    assert result['error']=='payment_required'
    assert events==['consume']
    assert PRIVATE not in json.dumps(result) and INTERNAL_URL not in json.dumps(result)


@pytest.mark.parametrize('tool',['arn_search_and_read','arn_search_company_and_read'])
def test_partial_failure_does_not_echo_internal_fields_or_exception(tools,tool):
    scope,client,license,events=tools
    client.failure=True
    result=scope[tool](**ARGS[tool])
    assert result['count']==1
    assert result['decisions'][0]['error']=='decision_unavailable'
    assert PRIVATE not in json.dumps(result) and INTERNAL_URL not in json.dumps(result)


@pytest.mark.parametrize('tool',sorted(TOOLS))
def test_signatures_preserved(tools,tool):
    scope,*_=tools
    wrapped=scope[tool]
    assert inspect.signature(wrapped)==inspect.signature(wrapped.__wrapped__)
    assert wrapped.__name__==tool


def test_only_r9_and_approved_r7_activity_changes_inside_six_tool_bodies():
    original=ast.parse((ROOT/'baseline/arn_mcp.py').read_text(encoding='utf-8'))
    candidate=ast.parse((ROOT/'arn_mcp.py').read_text(encoding='utf-8'))
    class Normalize(ast.NodeTransformer):
        def visit_FunctionDef(self,node):
            # R5's explicitly approved metadata is verified independently by tools/list.
            for d in node.decorator_list:
                if isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr=='tool':
                    d.keywords=[k for k in d.keywords if k.arg not in ('annotations','description')]
            return self.generic_visit(node)
        def visit_Dict(self,node):
            for k,v in zip(node.keys,node.values):
                if isinstance(k,ast.Constant) and k.value=='error':
                    if isinstance(v,ast.Call) and isinstance(v.func,ast.Name) and v.func.id in ('str','failure'):
                        node.values[node.values.index(v)]=ast.Constant('SAFE_PARTIAL_ERROR')
            return self.generic_visit(node)
    left=[n for n in original.body if isinstance(n,ast.FunctionDef) and n.name in TOOLS]
    right=[n for n in candidate.body if isinstance(n,ast.FunctionDef) and n.name in TOOLS]
    for node in left:
        identity=next(n for n in node.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='get_authenticated_user_id')
        # Permit exactly the separately tested R7 call, not arbitrary body changes.
        node.body.insert(node.body.index(identity)+1,ast.parse('license_manager.record_user_activity(user_id)').body[0])
        first = next(n for n in node.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='check')
        first.value.func.attr='consume'
        node.body=[n for n in node.body if n is first or not (isinstance(n,(ast.Assign,ast.Expr)) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='consume')]
        for item in ast.walk(node):
            if isinstance(item,ast.Constant) and isinstance(item.value,str):
                item.value=item.value.replace('10 fria sökningar','10 fria användningar')
    assert [ast.dump(Normalize().visit(n),include_attributes=False) for n in left]==[ast.dump(Normalize().visit(n),include_attributes=False) for n in right]


@pytest.mark.parametrize('tool',['arn_search','arn_get_decision'])
def test_uncaught_upstream_error_keeps_tool_error_without_session_url(tools,tool):
    scope,client,license,events=tools
    client.failure=True;client.search_failure=True
    from mcp.server.mcpserver.exceptions import ToolError
    with pytest.raises(ToolError) as error:
        scope[tool](**ARGS[tool])
    assert error.value.__suppress_context__ is True
    assert INTERNAL_URL not in str(error.value)
    assert json.loads(str(error.value))['error']=='result_unavailable'
    assert events.count('consume') == 1 and events[0] == 'consume'
