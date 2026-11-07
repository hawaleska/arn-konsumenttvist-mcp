"""No real customer data or credentials; admin selection is not identity proof."""
from copy import deepcopy
from unittest.mock import Mock
import pytest
from arn_license import LicenseManager


def setup():
    manager = object.__new__(LicenseManager)
    user = dict(user_id='synthetic-A', searches_used=4, paid=0,
                created_at=None, updated_at=None, last_user_activity_at=None, api_key_present=True)
    rows = [dict(id=i, user_id='synthetic-A', paypal_subscription_id='I-SYNTHETIC-'+str(i),
                 plan='monthly', status='CANCELLED', amount_sek=59,
                 started_at=None, expires_at=None, created_at=None, updated_at=None) for i in [1, 2]]
    response = dict(ok=True, schema_version=1, subject='synthetic-A', user=user, subscriptions=rows)
    manager._request = Mock(return_value=response)
    return manager, response


def test_all_stored_history_is_selected_without_secret_fields_or_mutation():
    manager, response = setup()
    response['user']['api_key_hash'] = 'SYNTHETIC_SECRET_CANARY'
    response['subscriptions'][0]['internal_session'] = 'SYNTHETIC_SESSION_CANARY'
    before = deepcopy(response)
    result = manager.get_subject_data('synthetic-A', verified_subject='synthetic-A')
    assert len(result['subscriptions']) == 2
    assert 'api_key_hash' not in result['user']
    assert 'internal_session' not in result['subscriptions'][0]
    assert response == before
    manager._request.assert_called_once_with('get_subject_data', user_id='synthetic-A')


@pytest.mark.parametrize('requested,verified', [('synthetic-A','synthetic-B'),(' synthetic-A',' synthetic-A'),
    ('',''),('A\0B','A\0B'),('x'*513,'x'*513),(None,None)])
def test_unverified_or_ambiguous_subject_never_reaches_backend(requested, verified):
    manager, _ = setup()
    with pytest.raises(PermissionError):
        manager.get_subject_data(requested, verified_subject=verified)
    manager._request.assert_not_called()


@pytest.mark.parametrize('target', ['subject','user','subscription'])
def test_backend_cannot_include_other_subject(target):
    manager, response = setup()
    if target == 'subject': response['subject'] = 'synthetic-B'
    elif target == 'user': response['user']['user_id'] = 'synthetic-B'
    else: response['subscriptions'][1]['user_id'] = 'synthetic-B'
    with pytest.raises(RuntimeError):
        manager.get_subject_data('synthetic-A', verified_subject='synthetic-A')


@pytest.mark.parametrize('change', ['negative_ok','missing_field','nested_value','no_user_with_rows','wrong_version'])
def test_incomplete_or_malformed_response_fails_closed(change):
    manager, response = setup()
    if change == 'negative_ok': response['ok'] = False
    elif change == 'missing_field': del response['subscriptions'][0]['expires_at']
    elif change == 'nested_value': response['user']['updated_at'] = {'sensitive':'synthetic'}
    elif change == 'no_user_with_rows': response['user'] = None
    else: response['schema_version'] = 2
    with pytest.raises(RuntimeError):
        manager.get_subject_data('synthetic-A', verified_subject='synthetic-A')


def test_no_persisted_subject_is_a_valid_empty_result():
    manager, response = setup();response.update(user=None, subscriptions=[])
    assert manager.get_subject_data('synthetic-A', verified_subject='synthetic-A') == {
        'subject':'synthetic-A','user':None,'subscriptions':[]}
