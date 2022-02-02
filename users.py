"""User operations for KFJC Trivia Robot."""

from model import db, connect_to_db, User
import common


def create_user(email, fname, password, salt):
    """Create and return a new user."""

    user = User(email=email, fname=fname, password=password, salt=salt)

    db.session.add(user)
    # Don't forget to call model.db.session.commit() when done adding items.

    return user


def get_users():
    """Return all users."""

    return User.query.all()


def get_user_by_id(user_id):
    """Return a user by primary key."""

    return User.query.get(user_id)


def get_user_by_email(email):
    """Return a user by email."""

    return User.query.filter(User.email == email).first()


def does_this_user_exist_already(email):
    """Return a boolean we can use for the if-statement in server.py."""

    if get_user_by_email(email):
        return True
    else:
        return False


def does_the_password_match(email, password):
    """Return a boolean we can use for the if-statement in server.py."""

    if User.query.filter(User.email == email, User.password == password).first():
        return True
    else:
        return False


def count_users():
    """How many unique users?"""

    return common.get_count(User.user_id, unique=True)
    



if __name__ == '__main__':
    """Will connect you to the database when you run users.py interactively"""
    from server import app
    connect_to_db(app)
