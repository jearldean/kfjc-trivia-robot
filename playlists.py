"""Playlist operations for KFJC Trivia Robot."""

from model import db, connect_to_db, Playlist
from random import choice
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
    """Get all playlists."""
    
    return Playlist.query.limit(limit_to).all()

def get_playlist_by_playlist_id(playlist_id):
    """Get a playlist by id. The primary key is not the station's playlist_id."""

    return Playlist.query.filter(Playlist.playlist_id == playlist_id).first()

def get_playlists_by_user_id(user_id):
    return Playlist.query.filter(Playlist.user_id == user_id).all()

def max_date_is_the_freshest_data_stamp():
    dto=db.session.query(Playlist.end_time.desc()).first()[0]
    return common.convert_datetime(datetime_object=dto)

def get_random_air_name():
    # tuple: (user_id, air_name)
    rando_user_id = choice(get_unique_user_ids())
    air_name = user_id_to_airname(user_id=rando_user_id)
    return (rando_user_id, air_name)

def all_air_names():
    dj_ids = get_unique_user_ids()
    air_names = []
    for di in dj_ids:
        air_names.append(user_id_to_airname(user_id=di))
    air_names.sort()
    return air_names

def get_unique_user_ids():
    dj_ids = []
    for val in db.session.query(Playlist.user_id.desc()).distinct():
        dj_ids.append(val[0])
    dj_ids.sort()
    return dj_ids

def user_id_to_airname(user_id):
    return Playlist.query.filter(Playlist.user_id == user_id).first().air_name



if __name__ == '__main__':
    """Will connect you to the database when you run playlists.py interactively"""
    from server import app
    connect_to_db(app)
