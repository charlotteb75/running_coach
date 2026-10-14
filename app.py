from flask import Flask, abort, request
from flask_migrate import Migrate
from errors import register_error_handlers
from models import Milestone, Training, TrainingDay, db
from schemas import MilestoneCreate, MilestoneUpdate, TrainingCreate, TrainingDayCreate, TrainingDayUpdate, TrainingUpdate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/running_coach"
register_error_handlers(app)
db.init_app(app)
migrate = Migrate(app, db)

@app.get("/training_day/<int:id_training_day>")
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
    return {"message": "success", "training_day": response}

@app.post("/training_day")
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

@app.patch("/training_day/<int:id_training_day>")
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
    return {"message": "Training day updated"}, 200

@app.get("/training/<int:id_training>")
def get_training(id_training):
    training = db.get_or_404(Training, id_training)
    response = {
        "training_type" : training.training_type,
        "training_duration" : training.training_duration,
        "content": training.content,
        "training_completed": training.training_completed,
        "feedback": training.feedback
    }
    return {"message": "success", "training": response}

@app.post("/training")
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

@app.patch("/training/<int:id_training>")
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
    return {"message": "Training updated"}, 200

@app.delete("/training/<int:id_training>")
def delete_training(id_training):
    training = db.get_or_404(Training, id_training)
    db.session.delete(training)
    db.session.commit()
    return {"message": "Training deleted"}, 200

@app.get("/milestone/<int:id_milestone>")
def get_milestone(id_milestone):
    milestone = db.get_or_404(Milestone, id_milestone)
    response = {
        "milestone_type" : milestone.milestone_type,
        "milestone_distance" : milestone.milestone_distance,
        "milestone_speed": milestone.milestone_speed,
        "date_estimated": milestone.date_estimated,
        "achieved": milestone.achieved,
        "date_achieved": milestone.date_achieved
    }
    return {"message": "success", "milestone": response}

@app.post("/milestone")
def create_milestone():
    milestone_data = MilestoneCreate.model_validate(request.get_json())
    milestone_obj = Milestone(**milestone_data.model_dump())
    db.session.add(milestone_obj)
    db.session.commit()
    return {
        "message": "success",
        "milestone": {
            "id_milestone": milestone_obj.id_milestone,
            "milestone_type": milestone_obj.milestone_type,
            "date_estimated": milestone_obj.date_estimated
        },
    }, 201

@app.patch("/milestone/<int:id_milestone>")
def update_milestone(id_milestone):
    data = MilestoneUpdate.model_validate(request.get_json())
    milestone = db.get_or_404(Milestone, id_milestone)
    
    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(milestone, field, value)

    db.session.commit()
    return {"message": "Milestone updated"}, 200

if __name__ == "__main__":
  app.run(debug=True)
