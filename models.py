from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Training(db.Model):
    __tablename__ = 'training'

    id_training = db.Column(db.Integer, primary_key=True)
    id_training_day = db.Column(db.Integer, db.ForeignKey('training_day.id_training_day'))
    training_type = db.Column(db.String(10))
    training_duration = db.Column(db.Integer)
    content = db.Column(db.Text, nullable=True)
    training_completed = db.Column(db.Boolean)
    feedback = db.Column(db.String(1000))

class TrainingDay(db.Model):
    __tablename__ = 'training_day'

    id_training_day = db.Column(db.Integer, primary_key=True)
    training_day_date = db.Column(db.Date)
    is_rest_day = db.Column(db.Boolean, nullable=False, default=True)

class Milestone(db.Model):
    __tablename__ = 'milestone'

    id_milestone = db.Column(db.Integer, primary_key=True)
    acheived = db.Column(db.Boolean)
    date_acheived = db.Column(db.Date)
    date_estimated = db.Column(db.Date)
    milestone_distance = db.Column(db.Float)
    milestone_speed = db.Column(db.Float)
    milestone_type = db.Column(db.String(10))

class RunningHistory(db.Model):
    __tablename__ = 'running_history'

    id_run = db.Column(db.Integer, primary_key=True)
    run_date = db.Column(db.Date)
    run_distance = db.Column(db.Float)
    run_time = db.Column(db.Float)
    run_speed = db.Column(db.Float)
    elevation = db.Column(db.Integer)

class Job(db.Model):
    __tablename__ = 'job'

    id_job = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String(10))
    job_duration = db.Column(db.Integer)
    success = db.Column(db.Boolean)
    status = db.Column(db.String(10))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
