import copy
import pytest
from arn_client import ARNClient
from arn_public_responses import public_tool_response

@pytest.mark.parametrize('text,hidden',[
 ('Konsumentens namn: Anna Andersson; köpet hävs.', 'Anna Andersson'),
 ('Privatpersonens namn: Eva Svensson\nSkälen kvarstår.', 'Eva Svensson'),
 ('Hemadress: Testgatan 12; köpet hävs.', 'Testgatan 12'),
 ('Bostadsadress: Testgatan 12, 123 45 Teststad\nSkälen kvarstår.', 'Testgatan 12'),
])
def test_explicit_private_fields_preserve_role_and_legal_content(text,hidden):
 result=ARNClient.minimize_identifiers(text)
 assert hidden not in result
 assert result.split(':',1)[0]==text.split(':',1)[0]
 assert result.endswith('köpet hävs.') or result.endswith('Skälen kvarstår.')
 assert ARNClient.minimize_identifiers(result)==result

@pytest.mark.parametrize('text',[
 'Företagets namn: Anna Andersson AB; köpet hävs.',
 'Leveransadress: Testgatan 12; leveransen är tvistig.',
 'Konsumentens namn: Anna Andersson yrkade att köpet hävs.',
 'ARN 2026-00123, datum 2026-11-10. Anna anser att felet är väsentligt.',
])
def test_ambiguous_text_company_and_material_address_are_not_guessed(text):
 assert ARNClient.minimize_identifiers(text)==text

def test_public_boundary_covers_decisions_common_cases_and_concepts_without_mutation():
 private='Konsumentens namn: Anna Andersson; köpet hävs.'
 value={'results':[{'case_number':'2026-00123','date':'2026-11-10','category':'Motor',
 'summary':private,'text':private,'score':1}],
 'common_cases':[{'description':private,'case_number':'2026-00123'}],
 'concepts':['synthetic@example.invalid']}
 before=copy.deepcopy(value);result=public_tool_response('arn_similar_cases',value)
 assert value==before and 'Anna Andersson' not in str(result) and 'synthetic@example.invalid' not in str(result)
 assert result['results'][0]['case_number']=='2026-00123'
 assert result['results'][0]['date']=='2026-11-10' and result['results'][0]['score']==1
 assert result['results'][0]['source']=='https://adokweb.arn.se/referatwebb'
 assert 'köpet hävs.' in result['common_cases'][0]['description']

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


def test_pdf_pages_minimized_and_stream_response_closed(monkeypatch):
 from unittest.mock import Mock
 import arn_client
 response=Mock(headers={'Content-Type':'application/pdf'},content=b'%PDF-SYNTHETIC')
 stream_seen=[]
 def reader(stream):
  stream_seen.append(stream)
  assert not stream.closed
  return Mock(pages=[Mock(extract_text=Mock(return_value='Konsumentens namn: Anna Andersson; köpet hävs.')),
                     Mock(extract_text=Mock(return_value='Skäl: fel i varan. E-post: a@example.invalid'))])
 monkeypatch.setattr(arn_client,'PdfReader',reader)
 text,pages=ARNClient._read_minimized_pdf(response)
 assert pages==2 and 'Anna Andersson' not in text and 'a@example.invalid' not in text
 assert 'köpet hävs.' in text and 'Skäl: fel i varan.' in text
 assert stream_seen[0].closed;response.close.assert_called_once()

@pytest.mark.parametrize('failure',['status','format','parser'])
def test_pdf_failure_closes_response_without_raw_error_content(monkeypatch,failure):
 from unittest.mock import Mock
 import arn_client
 response=Mock(headers={'Content-Type':'application/pdf'},content=b'%PDF-SYNTHETIC')
 if failure=='status':response.raise_for_status.side_effect=RuntimeError('synthetic-status')
 if failure=='format':response.headers={'Content-Type':'text/html'};response.content=b'SYNTHETIC-PRIVATE-NOT-PDF'
 if failure=='parser':monkeypatch.setattr(arn_client,'PdfReader',Mock(side_effect=ValueError('synthetic-parser')))
 with pytest.raises((RuntimeError,ValueError)):ARNClient._read_minimized_pdf(response)
 response.close.assert_called_once()

def test_metadata_failure_precedes_pdf_fetch(monkeypatch):
 from unittest.mock import Mock
 client=ARNClient();client.search=Mock(side_effect=RuntimeError('synthetic-source-unavailable'))
 client.session.get=Mock()
 with pytest.raises(RuntimeError):client.get_decision('2026-00001',file_id='1')
 client.session.get.assert_not_called()

def test_short_text_reference_is_not_silently_substituted_for_full_decision(monkeypatch):
 from unittest.mock import Mock
 client=ARNClient();events=[]
 def search(**kwargs):
  events.append('text-metadata')
  return [{'case_number':'2026-00001','file_id':'1','date':'2026-11-10','category':'Motor','summary':'Kort publicerat referat'}]
 client.search=search
 response=Mock()
 client.session.get=Mock(side_effect=lambda *a,**kw:(events.append('pdf') or response))
 monkeypatch.setattr(client,'_read_minimized_pdf',Mock(return_value=('Fullständiga sakskäl och utgång',3)))
 result=client.get_decision('2026-00001')
 assert events==['text-metadata','pdf']
 assert result['text']=='Fullständiga sakskäl och utgång' and result['summary']=='Kort publicerat referat'
 assert result['pages']==3 and result['date']=='2026-11-10'
