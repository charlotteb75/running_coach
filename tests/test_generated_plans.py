import json
import unittest
from datetime import date
from unittest.mock import patch

from flask import Flask
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.schemas.llm_schemas import validate_training_plan
from app.jobs.save_training_plan import save_training_plan
from app.jobs.generate_trainings import generate_training_job
from app.models import Training, TrainingDay, Milestone

TARGET = date(2026, 11, 3)


def training(kind="running", **changes):
    result = dict(id_training=None, training_type=kind, title="Séance", training_duration=30,
                  training_distance=4 if kind == "running" else None, description="Description de la séance")
    return result | changes


def payload(trainings=None, day="2026-11-03"):
    return dict(updated_training_days=[dict(training_day_date=day, trainings=trainings or [])],
                updated_milestones=[])


def validate(data):
    return validate_training_plan(json.dumps(data), TARGET)


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.init_app(self.app)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def test_validation(self):
        for entry in [training(training_duration=0), training(training_duration=True),
                      training(training_type="cycling"), training(training_distance=None),
                      training("strength", training_distance=2), training(title=" ")]:
            with self.subTest(entry=entry), self.assertRaises(ValidationError):
                validate(payload([entry]))
        with self.assertRaises(ValidationError):
            validate(payload([training(), training()]))
        with self.assertRaises(ValueError):
            validate(payload(day="2026-11-02"))
        with self.assertRaises(ValidationError):
            validate_training_plan('not json', TARGET)
        with self.assertRaises(ValidationError):
            validate(payload() | {'unexpected': 1})
        with self.assertRaises(ValidationError):
            validate_training_plan('```json\n'+json.dumps(payload())+'\n```', TARGET)

    def test_create_and_repeat_does_not_duplicate(self):
        plan = validate(payload([training()]))
        save_training_plan(plan, TARGET)
        day = db.session.scalar(db.select(TrainingDay))
        self.assertFalse(day.is_rest_day)
        row = db.session.scalar(db.select(Training))
        self.assertFalse(row.training_completed)
        self.assertIn('4 km', row.content)
        with self.assertRaises(ValueError):
            save_training_plan(plan, TARGET)
        self.assertEqual(db.session.query(Training).count(), 1)

    def test_rest_day_and_omissions(self):
        save_training_plan(validate(payload()), TARGET)
        self.assertTrue(db.session.scalar(db.select(TrainingDay)).is_rest_day)
        save_training_plan(validate(payload([training(), training('strength')])), TARGET)
        save_training_plan(validate(payload()), TARGET)
        self.assertEqual(db.session.query(Training).count(), 2)
        self.assertFalse(db.session.scalar(db.select(TrainingDay)).is_rest_day)
        run = db.session.scalar(db.select(Training).where(Training.training_type == 'running'))
        run.feedback = 'À conserver'
        db.session.commit()
        save_training_plan(validate(payload([training(id_training=run.id_training, training_duration=40)])), TARGET)
        self.assertEqual(run.training_duration, 40)
        self.assertEqual(run.feedback, 'À conserver')
        self.assertEqual(db.session.query(Training).count(), 2)

    def test_rollback_on_invalid_id_and_milestone(self):
        for data in [payload([training(id_training=999)]), payload([training()]) | {
            'updated_milestones': [dict(id_milestone=999, date_estimated='2026-12-01',
                                       milestone_type='distance', milestone_distance=10)]}]:
            with self.assertRaises(ValueError):
                save_training_plan(validate(data), TARGET)
            self.assertEqual(db.session.query(TrainingDay).count(), 0)
            self.assertEqual(db.session.query(Training).count(), 0)

    def test_completed_training_protected(self):
        save_training_plan(validate(payload([training()])), TARGET)
        run = db.session.scalar(db.select(Training))
        run.training_completed = True
        db.session.commit()
        with self.assertRaises(ValueError):
            save_training_plan(validate(payload([training(id_training=run.id_training, training_duration=40)])), TARGET)
        self.assertEqual(run.training_duration, 30)

    def test_milestone_update(self):
        milestone = Milestone(achieved=False, milestone_type='distance', milestone_distance=5)
        db.session.add(milestone)
        db.session.commit()
        data = dict(updated_training_days=[], updated_milestones=[dict(
            id_milestone=milestone.id_milestone, date_estimated='2026-12-01',
            milestone_type='distance', milestone_distance=10)])
        save_training_plan(validate(data), TARGET)
        self.assertEqual(milestone.milestone_distance, 10)
        milestone.achieved = True
        db.session.commit()
        with self.assertRaises(ValueError):
            save_training_plan(validate(data), TARGET)

    def test_commit_failure_rolls_back(self):
        with patch.object(db.session, 'commit', side_effect=SQLAlchemyError('test')):
            with self.assertRaises(SQLAlchemyError):
                save_training_plan(validate(payload([training()])), TARGET)
        self.assertEqual(db.session.query(TrainingDay).count(), 0)

    def test_job_with_mocked_llm(self):
        with patch('app.jobs.generate_trainings.generate_training_plan', return_value=validate(payload([training()]))) as llm:
            generate_training_job(TARGET)
            self.assertEqual(llm.call_args.args[0]['target_date'], TARGET.isoformat())
        self.assertEqual(db.session.query(Training).count(), 1)


if __name__ == '__main__':
    unittest.main()
