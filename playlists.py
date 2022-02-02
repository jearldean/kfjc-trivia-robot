"""Playlist operations for KFJC Trivia Robot."""

from random import randint  # , choice
import datetime

from model import db, connect_to_db, Playlist
import common


def create_playlist(playlist_id, user_id, air_name, start_time, end_time):
    """Create and return a new playlist."""

    playlist = Playlist(playlist_id=playlist_id, user_id=user_id, air_name=air_name,
        start_time=start_time, end_time=end_time)

    db.session.add(playlist)
    # Don't forget to call model.db.session.commit() when done adding items.

    return playlist


def get_playlists():
    """Get all playlists."""

    return Playlist.query.all()


def get_playlists_with_limit(limit_to=10):
    """Get all playlists. Option to limit."""
    
    return Playlist.query.limit(limit_to).all()


def get_playlist_by_playlist_id(playlist_id):
    """Get a playlist by id. 
    
    !!!The primary key is not the station's playlist_id.!!!"""

    return Playlist.query.filter(Playlist.playlist_id == playlist_id).first()


def get_playlists_by_user_id(user_id):
    """Shows by a DJ."""
    return Playlist.query.filter(Playlist.user_id == user_id).all()


def how_old_is_this_data():
    """Used to get the age of the data import:

    The datetime of the very last show on record."""

    return common.when_is_this_from(Playlist.end_time, newest=True)


def how_far_back_does_this_go():
    """What's the first show on record?
    
    earliest datestamp: datetime.datetime(1969, 12, 31, 16, 0)

    ??? Didn't give the right answer ???  '01/19/2022, 22:08:42' """

    #Playlist.query.order_by('updated desc').limit(1)
    many =  Playlist.query.order_by(Playlist.start_time).limit(100).all()
    #return common.when_is_this_from(Playlist.start_time, newest=False)
    for row in many:
        if row != '1969-12-31 16:00:00':
            print(row.start_time)
    #return many


def get_random_air_name():
    """
    
    tuple: (user_id, air_name)"""

    rando_user_id = randint(
        1, common.get_count(Playlist.user_id, unique=True))

    try:
        air_name = Playlist.query.filter(
            Playlist.user_id == rando_user_id).first().air_name
        return (rando_user_id, air_name)
    except AttributeError:
        # Bad row. Pick again:
        return get_random_air_name()


def user_id_to_airname(user_id):
    """Find the air_name for a DJ's user_id."""

    return Playlist.query.filter(Playlist.user_id == user_id).first().air_name


def count_playlists():
    """Counts rows in the table."""
    
    return common.get_count(Playlist.playlist_id, unique=False)


def get_random_playlist():
    """Returns one dj's show since 1995-09-19 22:00:00."""

    id_ = randint(1, common.get_count(Playlist.id_))
    return Playlist.query.get(id_)

def all_djs_birthdays():
    print_nice = ""
    for djid in range(1, common.get_count(Playlist.user_id, unique=True)):
        try:
            a, _, c= user_ids_first_playlist(user_id=djid)
            print_nice += a + "\t" + c + "\n"
            # print(user_ids_first_playlist(user_id=djid))
        except AttributeError:
            continue
        except TypeError:
            continue
    print(print_nice)
    #return print_nice

def user_ids_first_playlist(user_id=None):
    """When was {DJ}'s First Show?"""
    random_pick = False

    if user_id:
        air_name = user_id_to_airname(user_id=user_id)
    else:  # Give a random.
        random_pick = True
        user_id, air_name = get_random_air_name()
        while user_id == 222 or air_name.isspace():
            # Pick again; there are a couple of malformed rows.
            user_id, air_name = get_random_air_name()

    first_show = Playlist.query.order_by(Playlist.start_time).filter(
        Playlist.user_id == user_id).limit(1).first()
    first_show_date_object = first_show.start_time
    if first_show_date_object == datetime.datetime(1969, 12, 31, 16, 0):
        if random_pick:  # Pick again. Else, return nothing.
            return user_ids_first_playlist()
        else:
            return

    first_show_date = common.convert_datetime(
        first_show_date_object, human_readable=True)

    # return f"{air_name}'s first show was on {first_show_date}."
    return [air_name, first_show_date_object, first_show_date]


if __name__ == '__main__':
    """Will connect you to the database when you run playlists.py interactively"""
    from server import app
    connect_to_db(app)
