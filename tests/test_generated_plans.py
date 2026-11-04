import json
import pytest
from datetime import date
from unittest.mock import patch
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.schemas.llm_schemas import validate_training_plan
from app.jobs.save_training_plan import save_training_plan
from app.jobs.generate_trainings import generate_training_job
from app.models import Training, TrainingDay, Milestone
TARGET = date(2026, 11, 3)

def training(kind='running', **changes):
    result = dict(id_training=None, training_type=kind, title='Séance', training_duration=30, training_distance=4 if kind == 'running' else None, description='Description de la séance')
    return result | changes

def payload(trainings=None, day='2026-11-03'):
    return dict(updated_training_days=[dict(training_day_date=day, trainings=trainings or [])], updated_milestones=[])

def validate(data):
    return validate_training_plan(json.dumps(data), TARGET)

def test_create_and_repeat_does_not_duplicate(db_session):
    plan = validate(payload([training()]))
    save_training_plan(plan, TARGET)
    day = db_session.scalar(db.select(TrainingDay))
    assert not day.is_rest_day
    row = db_session.scalar(db.select(Training))
    assert not row.training_completed
    assert '4 km' in row.content
    with pytest.raises(ValueError):
        save_training_plan(plan, TARGET)
    assert db_session.query(Training).count() == 1

def test_rest_day_and_omissions(db_session):
    save_training_plan(validate(payload()), TARGET)
    assert db_session.scalar(db.select(TrainingDay)).is_rest_day
    save_training_plan(validate(payload([training(), training('strength')])), TARGET)
    save_training_plan(validate(payload()), TARGET)
    assert db_session.query(Training).count() == 2
    assert not db_session.scalar(db.select(TrainingDay)).is_rest_day
    run = db_session.scalar(db.select(Training).where(Training.training_type == 'running'))
    run.feedback = 'À conserver'
    db_session.commit()
    save_training_plan(validate(payload([training(id_training=run.id_training, training_duration=40)])), TARGET)
    assert run.training_duration == 40
    assert run.feedback == 'À conserver'
    assert db_session.query(Training).count() == 2

def test_rollback_on_invalid_id_and_milestone(db_session):
    for data in [payload([training(id_training=999)]), payload([training()]) | {'updated_milestones': [dict(id_milestone=999, date_estimated='2026-12-01', milestone_type='distance', milestone_distance=10)]}]:
        with pytest.raises(ValueError):
            save_training_plan(validate(data), TARGET)
        assert db_session.query(TrainingDay).count() == 0
        assert db_session.query(Training).count() == 0

def test_completed_training_protected(db_session):
    save_training_plan(validate(payload([training()])), TARGET)
    run = db_session.scalar(db.select(Training))
    run.training_completed = True
    db_session.commit()
    with pytest.raises(ValueError):
        save_training_plan(validate(payload([training(id_training=run.id_training, training_duration=40)])), TARGET)
    assert run.training_duration == 30

def test_milestone_update(db_session):
    milestone = Milestone(achieved=False, milestone_type='distance', milestone_distance=5)
    db_session.add(milestone)
    db_session.commit()
    data = dict(updated_training_days=[], updated_milestones=[dict(id_milestone=milestone.id_milestone, date_estimated='2026-12-01', milestone_type='distance', milestone_distance=10)])
    save_training_plan(validate(data), TARGET)
    assert milestone.milestone_distance == 10
    milestone.achieved = True
    db_session.commit()
    with pytest.raises(ValueError):
        save_training_plan(validate(data), TARGET)

def test_commit_failure_rolls_back(db_session):
    with patch.object(db_session, 'commit', side_effect=SQLAlchemyError('test')):
        with pytest.raises(SQLAlchemyError):
            save_training_plan(validate(payload([training()])), TARGET)
    assert db_session.query(TrainingDay).count() == 0

def test_job_with_mocked_llm(db_session):
    with patch('app.jobs.generate_trainings.generate_training_plan', return_value=validate(payload([training()]))) as llm:
        generate_training_job(TARGET)
        assert llm.call_args.args[0]['target_date'] == TARGET.isoformat()
    assert db_session.query(Training).count() == 1


@pytest.mark.parametrize("entry", [
    training(training_duration=0),
    training(training_duration=True),
    training(training_type="cycling"),
    training(training_distance=None),
    training("strength", training_distance=2),
    training(title=" "),
], ids=["zero-duration", "boolean-duration", "unknown-type", "missing-distance", "strength-distance", "blank-title"])
def test_invalid_training(entry):
    with pytest.raises(ValidationError):
        validate(payload([entry]))


@pytest.mark.parametrize("data", [payload([training(), training()]), payload() | {"unexpected": 1}],
                         ids=["duplicate-type", "unknown-field"])
def test_invalid_plan(data):
    with pytest.raises(ValidationError):
        validate(data)


def test_past_date():
    with pytest.raises(ValueError, match="before target_date"):
        validate(payload(day="2026-11-02"))


@pytest.mark.parametrize("content", ["not json", '```json\n' + json.dumps(payload()) + '\n```'],
                         ids=["malformed-json", "markdown-fences"])
def test_requires_raw_json(content):
    with pytest.raises(ValidationError):
        validate_training_plan(content, TARGET)
