from datetime import date
from unittest.mock import Mock

import pytest
import requests

from app.services.garmin import fetch_activities


@pytest.fixture
def garmin_get(monkeypatch):
    get = Mock()
    monkeypatch.setattr('app.services.garmin.requests.get', get)
    return get


def page_response(items):
    response = Mock()
    response.json.return_value = items
    return response


def test_fetch_all_pages(garmin_get):
    garmin_get.side_effect = [page_response([{'activityId': 1}]),
                             page_response([{'activityId': 2}]), page_response([])]
    assert fetch_activities('fake-token', date(2026, 11, 1), '2026-11-05') == [
        {'activityId': 1}, {'activityId': 2}]
    calls = garmin_get.call_args_list
    assert [call.kwargs['params']['start'] for call in calls] == [0, 1, 2]
    assert calls[0].kwargs['headers'] == {'Authorization': 'Bearer fake-token'}
    assert calls[0].kwargs['params']['startDate'] == '2026-11-01'
    assert calls[0].kwargs['params']['endDate'] == '2026-11-05'
    assert calls[0].kwargs['params']['activityType'] == 'running'


def test_empty_period(garmin_get):
    garmin_get.return_value = page_response([])
    assert fetch_activities('fake', '2026-11-01', '2026-11-05') == []
    garmin_get.return_value.raise_for_status.assert_called_once()


def test_http_error_does_not_return_partial_results(garmin_get):
    failure = page_response([])
    failure.raise_for_status.side_effect = requests.HTTPError('API error')
    garmin_get.side_effect = [page_response([{'activityId': 1}]), failure]
    with pytest.raises(requests.HTTPError):
        fetch_activities('fake', '2026-11-01', '2026-11-05')
    failure.json.assert_not_called()


@pytest.mark.parametrize('result', [{'error': 'unexpected response'}, None, [123]])
def test_invalid_response(garmin_get, result):
    garmin_get.return_value = page_response(result)
    with pytest.raises(ValueError, match='list of activities'):
        fetch_activities('fake', '2026-11-01', '2026-11-05')


def test_inverted_dates(garmin_get):
    with pytest.raises(ValueError, match='start_date'):
        fetch_activities('fake', '2026-11-05', '2026-11-01')
    garmin_get.assert_not_called()
