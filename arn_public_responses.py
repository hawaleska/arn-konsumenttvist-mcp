"""Explicit public contracts for the six ARN search/retrieval tools only."""

from datetime import datetime, timezone
from functools import wraps
import math
from arn_errors import public_error, raise_tool_error, error_context

DECISION_SOURCE = 'https://adokweb.arn.se/referatwebb'
COMMON_CASE_SOURCE = 'https://www.arn.se/vanligafall/'
TOOLS = frozenset((
    'arn_search', 'arn_get_decision', 'arn_search_and_read',
    'arn_search_company', 'arn_search_company_and_read', 'arn_similar_cases',
))
_DECISION_TEXT = ('case_number', 'date', 'category', 'summary', 'text')
_COMMON_TEXT = ('case_number', 'category', 'area', 'description')
_FILTER_TEXT = ('category', 'outcome', 'from_year', 'to_year')
_PAYMENT_MESSAGE = (
    'Du har använt dina 10 fria användningar. '
    'Fortsatt användning kräver en aktiv prenumeration. '
    'Välj mellan 59 SEK/månad eller 590 SEK/år genom '
    'verktyget arn_create_subscription för att få en säker '
    'PayPal-betalningslänk.'
)


def _text_fields(value, fields):
    return {key: value[key] for key in fields if type(value.get(key)) is str}


def _strings(value):
    return [item for item in value if type(item) is str] if type(value) is list else []


def public_license(value):
    if type(value) is not dict:
        return {}
    result = {}
    for key in ('allowed', 'paid', 'payment_required'):
        if type(value.get(key)) is bool:
            result[key] = value[key]
    for key in ('searches_used', 'free_searches', 'remaining'):
        item = value.get(key)
        if key in value and (type(item) is int and item >= 0 or key == 'remaining' and item is None):
            result[key] = item
    return result


def public_decision(value, *, similar=False):
    if type(value) is not dict:
        return None
    result = _text_fields(value, _DECISION_TEXT)
    if type(value.get('pages')) is int and value['pages'] >= 0:
        result['pages'] = value['pages']
    if similar:
        score = value.get('score')
        if type(score) is int or type(score) is float and math.isfinite(score):
            result['score'] = score
    result['source'] = DECISION_SOURCE
    if 'error' in value:
        result.update(public_error(value['error'], 'decision_unavailable', 'public_response'))
    return result


def _decisions(value, *, similar=False):
    if type(value) is not list:
        return []
    return [public_decision(item, similar=similar) for item in value if type(item) is dict]


def _common_cases(value):
    if type(value) is not list:
        return []
    result = []
    for item in value:
        if type(item) is not dict:
            continue
        public = _text_fields(item, _COMMON_TEXT)
        public['source'] = COMMON_CASE_SOURCE
        if 'error' in item:
            public.update(public_error(item['error'], 'decision_unavailable', 'public_response'))
        result.append(public)
    return result


def public_tool_response(tool, value):
    if tool not in TOOLS:
        raise ValueError('Unsupported public tool')
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    if type(value) is not dict:
        return {**public_error(None, 'result_unavailable', tool), 'retrieved_at': timestamp}
    if 'error' in value:
        payment = value['error'] == 'payment_required'
        result = {**public_error(value['error'], 'payment_required' if payment else 'result_unavailable', tool),
                  'retrieved_at': timestamp}
        if payment:
            result['message'] = _PAYMENT_MESSAGE
        if 'license' in value:
            result['license'] = public_license(value['license'])
        return result
    if tool == 'arn_similar_cases':
        result = {}
        result['concepts'] = _strings(value.get('concepts'))
        result['results'] = _decisions(value.get('results'), similar=True)
        result['common_cases'] = _common_cases(value.get('common_cases'))
        result['count'] = len(result['results'])
    elif tool == 'arn_get_decision':
        result = {'results': public_decision(value.get('results')) or
                  public_error(None, 'decision_unavailable', tool)}
    else:
        input_field = 'company' if 'company' in tool else 'query'
        fields = _FILTER_TEXT if input_field == 'company' else ()
        result = _text_fields(value, fields)
        collection = 'decisions' if tool.endswith('and_read') else 'results'
        result[collection] = _decisions(value.get(collection))
        result['count'] = len(result[collection])
    if 'license' in value:
        result['license'] = public_license(value['license'])
    result['retrieved_at'] = timestamp
    return result


def public_response(tool):
    """Run all internal work unchanged, then serialize every normal return branch."""
    if tool not in TOOLS:
        raise ValueError('Unsupported public tool')

    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            with error_context():
                try:
                    value = function(*args, **kwargs)
                    return public_tool_response(tool, value)
                except Exception as exc:
                    raise_tool_error(exc, tool)
        return wrapped
    return decorate
