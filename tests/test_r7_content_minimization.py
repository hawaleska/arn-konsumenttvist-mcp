import copy
import pytest
from arn_client import ARNClient
from arn_public_responses import public_tool_response

@pytest.mark.parametrize('text,hidden',[
 ('Kontakta synthetic.person@example.invalid; köpet hävs.', 'synthetic.person@example.invalid'),
 ('Personnummer: 19900101-0017; köpet hävs.', '19900101-0017'),
 ('Telefon: 070-1234567; köpet hävs.', '070-1234567')])
def test_targeted_redaction(text,hidden):
 result=ARNClient.minimize_identifiers(text)
 assert hidden not in result and result.endswith('; köpet hävs.')

@pytest.mark.parametrize('text',['2026-00001; 2026-11-04; 1200 kr; 14 dagar.', 'Anna anser att felet är väsentligt.', 'Diagnosen beskrivs.', 'Avtal 1234567890 och 590 SEK.'])
def test_meaning_and_limitations(text):
 assert ARNClient.minimize_identifiers(text)==text

@pytest.mark.parametrize('tool,field',[('arn_search','query'),('arn_search_company','company')])
def test_input_echo_removed(tool,field):
 value={field:'PRIVATE-INPUT','results':[{'case_number':'2026-00001','text':'Skälen'}]};before=copy.deepcopy(value)
 result=public_tool_response(tool,value)
 assert 'PRIVATE-INPUT' not in str(result) and field not in result
 assert result['results'][0]['text']=='Skälen' and value==before

def test_nested_query_echo_removed():
 result=public_tool_response('arn_similar_cases',{'problem':'PRIVATE','search_terms':['PRIVATE'],'concepts':['köp'],'results':[{'case_number':'2026-00001','matched_queries':['PRIVATE'],'score':2}],'common_cases':[]})
 assert 'PRIVATE' not in str(result) and result['concepts']==['köp'] and result['results'][0]['score']==2

def test_search_before_request(monkeypatch):
 client=ARNClient();seen=[];original=client.minimize_identifiers
 monkeypatch.setattr(client,'minimize_identifiers',lambda text:(seen.append(original(text)) or seen[-1]))
 def stop(*a,**k):raise RuntimeError('synthetic-stop')
 monkeypatch.setattr(client.session,'get',stop)
 with pytest.raises(RuntimeError,match='synthetic-stop'):client.search('Personnummer: 19900101-0017')
 assert seen==['Personnummer: [identifierare maskerad]']

@pytest.mark.parametrize('text,ending',[
 ('Telefon: 070-1234567 1200 kr ska återbetalas.', ' 1200 kr ska återbetalas.'),
 ('Telefon: 0701234567 14 dagar gäller.', ' 14 dagar gäller.'),
])
def test_phone_redaction_never_consumes_following_amount_or_deadline(text,ending):
 result=ARNClient.minimize_identifiers(text)
 assert result=='Telefon: [telefon maskerad]'+ending

def test_ambiguous_numeric_reference_not_treated_as_phone():
 text='Telefon: 1234567890 är ett artikelnummer i underlaget.'
 assert ARNClient.minimize_identifiers(text)==text
