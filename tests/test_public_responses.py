import copy
from datetime import datetime
import json

import pytest

from arn_public_responses import (public_tool_response,public_decision,public_license,
                                 DECISION_SOURCE,COMMON_CASE_SOURCE,TOOLS)
from conftest import decision,license_status,PRIVATE,INTERNAL_URL


def payload(tool):
    data={'query':'test','company':'test','category':'Test','outcome':'Test',
          'from_year':'2020','to_year':'2026','problem':'test','concepts':['test',{'x':PRIVATE}],
          'search_terms':['test'],'count':99,'license':license_status(),'unexpected':PRIVATE}
    data['results']=decision() if tool=='arn_get_decision' else [decision()]
    data['decisions']=[decision()]
    data['common_cases']=[{'case_number':'test','description':'Test','source':INTERNAL_URL,'unknown':PRIVATE}]
    return data


@pytest.mark.parametrize('tool',sorted(TOOLS))
def test_explicit_schema_and_no_mutation(tool):
    raw=payload(tool);before=copy.deepcopy(raw)
    response=public_tool_response(tool,raw)
    encoded=json.dumps(response)
    assert PRIVATE not in encoded and INTERNAL_URL not in encoded
    assert raw==before
    assert datetime.fromisoformat(response['retrieved_at'].replace('Z','+00:00')).utcoffset().total_seconds()==0
    if tool=='arn_get_decision':assert isinstance(response['results'],dict)
    else:
        key='decisions' if tool.endswith('and_read') else 'results'
        assert response['count']==len(response[key])==1
    if tool=='arn_similar_cases':assert response['common_cases'][0]['source']==COMMON_CASE_SOURCE


@pytest.mark.parametrize('tool',sorted(TOOLS))
def test_payment_and_unknown_error_branches(tool):
    for error in ('payment_required',INTERNAL_URL):
        response=public_tool_response(tool,{'error':error,'message':INTERNAL_URL,'license':license_status(False),'unknown':PRIVATE})
        assert PRIVATE not in json.dumps(response) and INTERNAL_URL not in json.dumps(response)
        assert response['error']==('payment_required' if error=='payment_required' else 'result_unavailable')
        assert response['license']['allowed'] is False


@pytest.mark.parametrize('value',[None,1,'bad',[],True])
def test_malformed_root_is_neutral(value):
    assert public_tool_response('arn_search',value)['error']=='result_unavailable'


def test_nested_types_cannot_smuggle_objects():
    raw=decision();raw.update(summary={'secret':PRIVATE},pages=True,score=float('inf'),matched_queries=[{'url':INTERNAL_URL},'test'],error=INTERNAL_URL)
    result=public_decision(raw,similar=True)
    assert 'summary' not in result and 'pages' not in result and 'score' not in result
    assert result['matched_queries']==['test']
    assert result['error']=='decision_unavailable'
    assert result['source']==DECISION_SOURCE
    assert PRIVATE not in json.dumps(result) and INTERNAL_URL not in json.dumps(result)


def test_license_types_are_explicit():
    assert public_license({'allowed':1,'paid':False,'remaining':None,'searches_used':True,'free_searches':-1,'user_id':PRIVATE})=={'paid':False,'remaining':None}


@pytest.mark.parametrize('tool',['arn_search','arn_search_and_read','arn_search_company','arn_search_company_and_read','arn_similar_cases'])
def test_empty_and_bad_collections(tool):
    raw=payload(tool)
    raw['results']=None;raw['decisions']=[None,PRIVATE,[]];raw['common_cases']=[None,PRIVATE]
    response=public_tool_response(tool,raw)
    key='decisions' if tool.endswith('and_read') else 'results'
    assert response[key]==[] and response['count']==0
    assert PRIVATE not in json.dumps(response)


def test_get_decision_malformed_object_keeps_object_contract():
    result=public_tool_response('arn_get_decision',{'results':[]})
    assert isinstance(result['results'],dict) and result['results']['error']=='decision_unavailable'


def test_similarity_metadata_preserved():
    response=public_tool_response('arn_similar_cases',{'problem':'test','concepts':['mobil'],'search_terms':['test'],'results':[{**decision(),'score':12.5,'matched_queries':['mobil']}],'common_cases':[]})
    assert response['results'][0]['score']==12.5
    assert response['results'][0]['matched_queries']==['mobil']
    assert response['concepts']==['mobil']


def test_unsupported_tool_refused():
    with pytest.raises(ValueError):public_tool_response('arn_create_subscription',{})
