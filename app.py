from flask import Flask
from flask_migrate import Migrate
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/running_coach"
db.init_app(app)
migrate = Migrate(app, db)

@app.route("/training_day", methods=["GET"])
def get_training_day():
    pass


if __name__ == "__main__":
  app.run(debug=True)
