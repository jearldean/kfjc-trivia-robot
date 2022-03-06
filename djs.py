"""DJ operations for KFJC Trivia Robot."""

from model import db, connect_to_db, Dj
import common

WHITE_HEART_EMOJI = '♡'
# TODO Couldn't get real emojis to work.

def create_dj(dj_id, air_name, administrative, silent_mic):
    """Create and return a new dj."""

    dj = Dj(
        dj_id=dj_id,
        air_name=air_name,
        administrative=administrative,
        silent_mic=silent_mic)

    db.session.add(dj)
    # Don't forget to call model.db.session.commit() when done adding items.

    return dj


def get_dj_id_by_id(dj_id):
    """Return a dj by primary key."""

    return Dj.query.get(dj_id)


def get_airname_for_dj(dj_id, posessive=False):
    """Return an air_name by primary key."""

    dj = Dj.query.get(dj_id)
    air_name = dj.air_name

    if dj.silent_mic:
        # Add white heart emojis for our DJs that have passed on:
        if posessive:
            suffix = common.the_right_apostrophe(air_name=air_name)
            return f"{WHITE_HEART_EMOJI} {dj.air_name}{suffix} {WHITE_HEART_EMOJI}"
        else:
            return f"{WHITE_HEART_EMOJI} {dj.air_name} {WHITE_HEART_EMOJI}"
    else:
        if posessive:
            suffix = common.the_right_apostrophe(air_name=air_name)
            return dj.air_name + suffix
        else:
            return dj.air_name


if __name__ == '__main__':
    """Will connect you to the database when you run djs.py interactively"""
    from server import app
    connect_to_db(app)
