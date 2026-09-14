from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/running_coach"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.route("/training_day", methods=["GET"])
def get_training_day():
    pass


if __name__ == "__main__":
  app.run(debug=True)
