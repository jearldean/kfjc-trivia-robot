"""Models for KFJC Trivia Robot."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
DATABASE = "trivia"


class User(db.Model):
    """A user."""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    fname = db.Column(db.String(30), unique=False, nullable=True)
    password = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable=False)
    # user_answers = a list of UserAnswer objects

    def __repr__(self):
        spaces = (13 - len(self.fname)) * " "
        return (f"\nU:{self.user_id}\t{self.fname}{spaces}{self.email}")


class Question(db.Model):
    """A question."""

    __tablename__ = 'questions'

    question_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    question = db.Column(db.String, nullable=False)
    acceptable_answers = db.Column(db.PickleType, nullable=False)
    # user_answers = a list of UserAnswers objects

    def __repr__(self):
        spaces = (25 - len(self.question)) * " "
        return (f"\nQ:{self.question_id}\t{self.question}{spaces}{self.acceptable_answers}")


class UserAnswer(db.Model):
    """A response from a user."""

    __tablename__ = 'user_answers'

    user_answer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    question_id = db.Column(db.Integer, db.ForeignKey("questions.question_id"))
    answer_given = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True)

    question = db.relationship("Question", backref="user_answers")
    user = db.relationship("User", backref="user_answers")

    def __repr__(self):
        return f"\nA:{self.user_answer_id}\tU:{self.user_id}\tQ:{self.question_id}\t{self.timestamp}\t{self.answer_given}"


def connect_to_db(flask_app, db_uri=f"postgresql:///{DATABASE}", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print(f"Connected to {db_uri}")


if __name__ == "__main__":
    from server import app

    connect_to_db(app)
