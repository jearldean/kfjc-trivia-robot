"""User operations for KFJC Trivia Robot."""

import bcrypt

from model import db, connect_to_db, User

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


def create_a_user(username, fname, password):
    """Check for user existence, create if new user."""

    if not does_user_exist_already(username):
        utf8_password = password.encode('utf-8')
        new_user = create_user(
            username=username,
            fname=fname,
            password=utf8_password)
        db.session.commit()
        return new_user
    else:
        return False


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
    
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)
    
    
if __name__ == '__main__':
    """Will connect you to the database when you run users.py interactively"""
    from server import app
    connect_to_db(app)
