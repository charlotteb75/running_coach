from flask import Flask, request
from flask_migrate import Migrate
from errors import register_error_handlers
from models import Training, TrainingDay, db
from schemas import TrainingCreate, TrainingDayCreate

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

@app.post("/training_day/<int:id_training_day>")
def create_training_day():
    training_day_data = TrainingDayCreate.model_validate(request.get_json())
    training_day_obj = TrainingDay(**training_day_data.model_dump())
    db.session.add(training_day_obj)
    db.session.commit()
    return {"message": "success", "training_day": training_day_obj}

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

@app.post("/training/<int:id_training>")
def create_training():
    training_data = TrainingCreate.model_validate(request.get_json())
    training_obj = Training(**training_data.model_dump())
    db.session.add(training_obj)
    db.session.commit()
    return {"message": "success", "training_day": training_obj}



if __name__ == "__main__":
  app.run(debug=True)
