

from flask import Blueprint, abort, request
from app.extensions import db
from app.models import Training, TrainingDay
from app.schemas import TrainingDayCreate, TrainingDayUpdate


training_day_bp = Blueprint("training_day", __name__)

@training_day_bp.get("/training_day/<int:id_training_day>")
def get_training_day(id_training_day):
    training_day = db.get_or_404(TrainingDay, id_training_day)
    total_duration = db.session.scalar(
        db.select(db.func.coalesce(db.func.sum(Training.training_duration), 0))
        .where(Training.id_training_day == id_training_day)
    )
    trainings = db.session.scalars(db.select(Training).where(
        Training.id_training_day == id_training_day
        )
    ).all()
    completed = bool(trainings) and all(
        training.training_completed is True
        for training in trainings
    )
    response = {
        "is_rest_day" : training_day.is_rest_day,
        "training_day_duration": total_duration,
        "training_day_completed": completed
    }
    return {
        "message": "success",
        "training_day": response
        }

@training_day_bp.post("/training_day")
def create_training_day():
    training_day_data = TrainingDayCreate.model_validate(request.get_json())
    training_day_obj = TrainingDay(**training_day_data.model_dump())
    db.session.add(training_day_obj)
    db.session.commit()
    return {
        "message": "success",
        "training_day": {
            "id_training_day": training_day_obj.id_training_day,
            "training_day_date": training_day_obj.training_day_date.isoformat(),
            "is_rest_day": training_day_obj.is_rest_day,
        },
    }, 201

@training_day_bp.patch("/training_day/<int:id_training_day>")
def update_training_day(id_training_day):
    data = TrainingDayUpdate.model_validate(request.get_json())
    training_day = db.get_or_404(TrainingDay, id_training_day)
    
    if data.is_rest_day == True:
        training_id = db.session.scalar(
            db.select(Training.id_training)
            .where(Training.id_training_day == id_training_day)
            .limit(1)
        )
        if training_id is not None:
            abort(409, description="This training day has trainings")

    training_day.is_rest_day = data.is_rest_day
    db.session.commit()
    return {
        "message": "Training day updated"
        }, 200