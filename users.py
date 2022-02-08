"""User operations for KFJC Trivia Robot."""

from model import db, connect_to_db, User
import bcrypt
import common

def create_user(username, fname, password):
    """Create and return a new user."""

    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    user = User(
        username=username,
        fname=fname,
        hashed_password=hashed_password)

    db.session.add(user)
    # Don't forget to call model.db.session.commit() when done adding items.

    return user


def get_users():
    """Return all users."""

    return User.query.all()


def get_user_by_id(user_id):
    """Return a user by primary key."""

    return User.query.get(user_id)


def get_user_by_username(username):
    """Return a user by username."""

    return User.query.filter(User.username == username).first()


def does_user_exist_already(username):
    """Return a boolean we can use for the if-statement in server.py."""

    if get_user_by_username(username):
        return True
    else:
        return False


def does_password_match(plain_text_password, hashed_password):
    """Check hashed password. Returns boolean.
    # Using bcrypt, the salt is saved into the hash itself
    """
    
    return bcrypt.checkpw(plain_text_password, hashed_password)


def count_users():
    """How many unique users?"""

    return common.get_count(User.user_id, unique=True)
    
    
if __name__ == '__main__':
    """Will connect you to the database when you run users.py interactively"""
    from server import app
    connect_to_db(app)
