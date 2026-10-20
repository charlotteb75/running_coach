from flask import Flask
from app.extensions import db, migrate
from app.routes.training import training_bp
from app.routes.training_day import training_day_bp
from app.routes.milestone import milestone_bp
from app.routes.running_history import running_history_bp
from app.routes.job import job_bp
from app.errors import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/running_coach"
    register_error_handlers(app)
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(training_bp)
    app.register_blueprint(training_day_bp)
    app.register_blueprint(milestone_bp)
    app.register_blueprint(running_history_bp)
    app.register_blueprint(job_bp)
    return app

