from datetime import date, timedelta
from app.services.openrouter import generate_training_plan
from app.models import Milestone, RunningHistory, Training, TrainingDay
from app.extensions import db


def _serialize_rows(statement):
    rows = db.session.execute(statement).mappings().all()
    return [
        {
            key: value.isoformat() if isinstance(value, date) else value
            for key, value in row.items()
        }
        for row in rows
    ]


def build_training_context(target_date):
    start_date = target_date - timedelta(days=7)

    active_milestones = db.select(*Milestone.__table__.columns).where(
        Milestone.achieved.is_(False)
    ).order_by(Milestone.date_estimated, Milestone.id_milestone)

    recently_achieved_milestones = db.select(*Milestone.__table__.columns).where(
        Milestone.achieved.is_(True)
    ).order_by(Milestone.date_estimated, Milestone.id_milestone).limit(5)

    trainings = db.select(
        *Training.__table__.columns,
        TrainingDay.training_day_date,
    ).join(TrainingDay, Training.id_training_day == TrainingDay.id_training_day)

    recent_trainings = trainings.where(
        TrainingDay.training_day_date >= start_date,
        TrainingDay.training_day_date < target_date,
    ).order_by(TrainingDay.training_day_date, Training.id_training)

    recent_runs = db.select(*RunningHistory.__table__.columns).where(
        RunningHistory.run_date >= start_date,
        RunningHistory.run_date < target_date,
    ).order_by(RunningHistory.run_date, RunningHistory.id_run)

    planned_trainings = trainings.where(
        TrainingDay.training_day_date >= target_date
    ).order_by(TrainingDay.training_day_date, Training.id_training)

    return {
        "target_date": target_date.isoformat(),
        "active_milestones": _serialize_rows(active_milestones),
        "recently_achieved_milestones": _serialize_rows(recently_achieved_milestones),
        "recent_trainings": _serialize_rows(recent_trainings),
        "recent_runs": _serialize_rows(recent_runs),
        "planned_trainings": _serialize_rows(planned_trainings),
    }


def generate_training_job():
    target_date = date.today() + timedelta(days=1)
    context = build_training_context(target_date)
    plan = generate_training_plan(context)
    return plan
