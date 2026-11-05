import ast
import types
from pathlib import Path
from unittest.mock import Mock

import jwt
import pytest

from arn_errors import safe_exception
from conftest import ROOT,INTERNAL_URL
from test_error_contract import assert_clean


@pytest.mark.parametrize('tool',['arn_search','arn_get_decision','arn_search_and_read','arn_search_company','arn_search_company_and_read','arn_similar_cases'])
def test_success_serializer_is_identical_to_approved_r3(tool,monkeypatch):
    import arn_public_responses as current
    from datetime import datetime,timezone
    from test_public_responses import payload
    baseline=types.ModuleType('approved_r3_serializer')
    exec(compile((ROOT/'baseline/arn_public_responses.py').read_text(encoding='utf-8'),'approved_r3','exec'),baseline.__dict__)
    class Clock:
        @staticmethod
        def now(zone):return datetime(2026,11,3,0,0,0,tzinfo=timezone.utc)
    monkeypatch.setattr(current,'datetime',Clock)
    baseline.datetime=Clock
    data=payload(tool)
    expected=baseline.public_tool_response(tool,data)
    # Approved R7 change: only redundant raw input echoes are removed.
    for key in ('query','company','problem','search_terms'):
        expected.pop(key,None)
    for item in expected.get('results',[]):
        if isinstance(item,dict):item.pop('matched_queries',None)
    assert current.public_tool_response(tool,data)==expected


@pytest.mark.parametrize('category',[ValueError,PermissionError,RuntimeError])
def test_existing_r2_api_key_verifier_still_fails_closed(category,caplog):
    tree=ast.parse((Path(__file__).with_name('auth_reference.py')).read_text(encoding='utf-8'))
    node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARNTokenVerifier')
    manager=Mock()
    manager.user_id_from_api_key.side_effect=safe_exception(category,'backend_unavailable','license_request',RuntimeError(INTERNAL_URL))
    class AccessToken(types.SimpleNamespace):pass
    scope={'LicenseManager':lambda:manager,'AccessToken':AccessToken,'jwt':jwt,'PyJWTError':jwt.PyJWTError}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'unchanged_arn_auth','exec'),scope)
    import asyncio
    verifier=scope['ARNTokenVerifier']()
    if category is ValueError:
        assert asyncio.run(verifier.verify_token('synthetic-api-key')) is None
    else:
        with pytest.raises(category) as raised:asyncio.run(verifier.verify_token('synthetic-api-key'))
        assert_clean(str(raised.value))
    assert_clean(caplog.text)
