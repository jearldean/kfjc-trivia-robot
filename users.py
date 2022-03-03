"""User operations for KFJC Trivia Robot."""

import bcrypt

from model import db, connect_to_db, User

def create_user(username, fname, password):
    """Create and return a new user."""
    user = User(
        username=username,
        fname=fname,
        hashed_password=hash_it(password))

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
        new_user = create_user(
            username=username,
            fname=fname,
            password=password)
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


def does_password_match(user_instance, password_from_form):
    """Check hashed password. Returns boolean."""
    
    if bcrypt.checkpw(
            password_from_form.encode('utf8'),
            user_instance.hashed_password.encode('utf8')):
        print("match")
        return True
    else:
        print("does not match")
        return False
        
    
def hash_it(password):
    """Problems using bcrypt."""
    # flask_bcrypt.generate_password_hash(password).decode('utf8')
    salt = bcrypt.gensalt()
    # Using bcrypt, the salt is saved into the hash itself
    hashed = bcrypt.hashpw(password.encode('utf8'), salt)
    hashed_password = hashed.decode('utf8') # decode the hash to prevent being encoded twice
    return hashed_password


if __name__ == '__main__':
    """Will connect you to the database when you run users.py interactively"""
    from server import app
    connect_to_db(app)
