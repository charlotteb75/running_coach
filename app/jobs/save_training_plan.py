"""Apply a validated plan atomically; omitted entries are never deleted."""

from sqlalchemy import text

from app.extensions import db
from app.schemas.llm_schemas import GeneratedPlan, validate_training_plan
from app.models import Milestone, Training, TrainingDay


def _training_content(training):
    parts = [training.title]
    if training.training_distance is not None:
        parts.append(f"Distance : {training.training_distance:g} km")
    parts.append(training.description)
    return "\n\n".join(parts)


def save_training_plan(plan: GeneratedPlan, target_date):
    try:
        plan = validate_training_plan(plan.model_dump_json(), target_date)

        for generated_day in plan.updated_training_days:
            day = db.session.execute(
                db.select(TrainingDay)
                .where(TrainingDay.training_day_date == generated_day.training_day_date)
                .with_for_update()
            ).scalar_one_or_none()
            if day is None:
                day = TrainingDay(
                    training_day_date=generated_day.training_day_date,
                    is_rest_day=True,
                )
                db.session.add(day)
                db.session.flush()

            existing_trainings = db.session.scalars(
                db.select(Training).where(Training.id_training_day == day.id_training_day)
                .with_for_update()
            ).all()
            by_id = {training.id_training: training for training in existing_trainings}
            updates = {t.id_training: t for t in generated_day.trainings if t.id_training is not None}
            for training_id in updates:
                if training_id not in by_id:
                    raise ValueError("Training ID does not belong to this day")
                if by_id[training_id].training_completed:
                    raise ValueError("Completed trainings cannot be modified")

            types = [updates[t.id_training].training_type if t.id_training in updates
                     else t.training_type for t in existing_trainings]
            types.extend(t.training_type for t in generated_day.trainings if t.id_training is None)
            if len(types) != len(set(types)):
                raise ValueError("A training of this type already exists; provide its id_training to update it")

            for generated in generated_day.trainings:
                if generated.id_training is None:
                    training = Training(
                        id_training_day=day.id_training_day,
                        training_completed=False,
                        feedback=None,
                    )
                    db.session.add(training)
                else:
                    training = by_id[generated.id_training]
                training.training_type = generated.training_type
                training.training_duration = generated.training_duration
                training.content = _training_content(generated)
            day.is_rest_day = not types

        for generated in plan.updated_milestones:
            milestone = db.session.execute(
                db.select(Milestone).where(Milestone.id_milestone == generated.id_milestone)
                .with_for_update()
            ).scalar_one_or_none()
            if milestone is None:
                raise ValueError("Unknown milestone ID")
            if milestone.achieved:
                raise ValueError("Achieved milestones cannot be modified")
            milestone.date_estimated = generated.date_estimated
            milestone.milestone_type = generated.milestone_type
            milestone.milestone_distance = generated.milestone_distance
            milestone.milestone_speed = generated.milestone_speed

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
