

from flask import Blueprint, request
from app.extensions import db
from app.models import Training, TrainingDay
from app.schemas import TrainingCreate, TrainingUpdate


training_bp = Blueprint("training", __name__)


@training_bp.get("/training/<int:id_training>")
def get_training(id_training):
    training = db.get_or_404(Training, id_training)
    response = {
        "training_type" : training.training_type,
        "training_duration" : training.training_duration,
        "content": training.content,
        "training_completed": training.training_completed,
        "feedback": training.feedback
    }
    return {
        "message": "success",
        "training": response
        }

@training_bp.post("/training")
def create_training():
    training_data = TrainingCreate.model_validate(request.get_json())
    training_day = db.get_or_404(TrainingDay, training_data.id_training_day)
    training_day.is_rest_day = False
    training_obj = Training(**training_data.model_dump())
    db.session.add(training_obj)
    db.session.commit()
    return {
        "message": "success",
        "training": {
            "id_training": training_obj.id_training,
            "id_training_day": training_obj.id_training_day,
            "training_type": training_obj.training_type
        },
    }, 201

@training_bp.patch("/training/<int:id_training>")
def update_training(id_training):
    data = TrainingUpdate.model_validate(request.get_json())
    training = db.get_or_404(Training, id_training)
    
    changes = data.model_dump(exclude_unset=True)

    if changes.get("id_training_day") is not None:
        target_training_day = db.get_or_404(TrainingDay, changes["id_training_day"])
        target_training_day.is_rest_day = False

    for field, value in changes.items():
        setattr(training, field, value)

    db.session.commit()
    return {
        "message": "Training updated"
        }, 200

@training_bp.delete("/training/<int:id_training>")
def delete_training(id_training):
    training = db.get_or_404(Training, id_training)
    db.session.delete(training)
    db.session.commit()
    return {
        "message": "Training deleted"
        }, 200