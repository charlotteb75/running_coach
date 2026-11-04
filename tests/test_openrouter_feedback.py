import json
import pytest
from types import SimpleNamespace
from pydantic import ValidationError
from app.services.openrouter import generate_training_plan
VALID = json.dumps({'updated_training_days': [], 'updated_milestones': []})

def response(content, finish='stop'):
    return SimpleNamespace(choices=[SimpleNamespace(finish_reason=finish, message=SimpleNamespace(content=content))])

def run_plan():
    return generate_training_plan({'target_date': '2026-11-03'})

def test_valid_first_response(openrouter_client):
    openrouter_client.chat.completions.create.return_value = response(VALID)
    assert run_plan().updated_training_days == []
    assert openrouter_client.chat.completions.create.call_count == 1

def test_json_then_schema_error_then_success(openrouter_client):
    invalid = json.dumps({'updated_training_days': [], 'updated_milestones': [{'id_milestone': 'ms_5k', 'date_estimated': '2026-12-01', 'milestone_type': 'distance', 'milestone_distance': 5}]})
    openrouter_client.chat.completions.create.side_effect = [response('bad json'), response(invalid), response(VALID)]
    run_plan()
    calls = openrouter_client.chat.completions.create.call_args_list
    assert [len(c.kwargs['messages']) for c in calls] == [2, 4, 6]
    assert calls[1].kwargs['messages'][2]['content'] == 'bad json'
    assert 'updated_milestones.0.id_milestone' in calls[2].kwargs['messages'][-1]['content']

def test_date_error_feedback(openrouter_client):
    old = json.dumps({'updated_training_days': [{'training_day_date': '2026-01-01', 'trainings': []}], 'updated_milestones': []})
    openrouter_client.chat.completions.create.side_effect = [response(old), response(VALID)]
    run_plan()
    assert 'before target_date' in openrouter_client.chat.completions.create.call_args.kwargs['messages'][-1]['content']

def test_stops_after_three_invalid_responses(openrouter_client):
    openrouter_client.chat.completions.create.return_value = response('invalid')
    with pytest.raises(ValidationError):
        run_plan()
    assert openrouter_client.chat.completions.create.call_count == 3

def test_api_error_is_not_corrected(openrouter_client):
    openrouter_client.chat.completions.create.side_effect = RuntimeError('API unavailable')
    with pytest.raises(RuntimeError, match='API unavailable'):
        run_plan()
    assert openrouter_client.chat.completions.create.call_count == 1


@pytest.mark.parametrize("result", [response(''), response(VALID, 'length'), SimpleNamespace(choices=[])],
                         ids=["empty-content", "truncated", "no-choices"])
def test_empty_and_incomplete_responses_are_not_corrected(openrouter_client, result):
    openrouter_client.chat.completions.create.return_value = result
    with pytest.raises(RuntimeError):
        run_plan()
    assert openrouter_client.chat.completions.create.call_count == 1
