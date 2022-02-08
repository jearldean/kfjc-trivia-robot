"""Playlist operations for KFJC Trivia Robot."""

from random import choice, sample
from collections import OrderedDict

from model import db, connect_to_db, Playlist
import common


def create_playlist(kfjc_playlist_id, dj_id, air_name, start_time, end_time):
    """Create and return a new playlist."""

    playlist = Playlist(
        kfjc_playlist_id = kfjc_playlist_id,
        dj_id = dj_id,
        air_name = air_name,
        start_time = start_time,
        end_time = end_time)

    db.session.add(playlist)
    # Don't forget to call model.db.session.commit() when done adding items.

    return playlist


def get_playlists():
    """Get all playlists."""

    return Playlist.query.all()


def get_playlists_with_limit(limit_to=10):
    """Get all playlists. Option to limit."""
    
    return Playlist.query.limit(limit_to).all()


def get_playlist_by_kfjc_playlist_id(kfjc_playlist_id):
    """Get a playlist by kfjc_playlist_id."""

    return Playlist.query.filter(Playlist.kfjc_playlist_id == kfjc_playlist_id).first()


def get_all_dj_ids():
    """Info about our brotherhood of KFJC DJs."""

    raw_q = db.session.query(Playlist.dj_id).distinct()
    unique_dj_ids = [row[0] for row in raw_q.all()]
    unique_dj_ids.sort()
    count_dj_ids = len(unique_dj_ids)
    return unique_dj_ids, count_dj_ids
    

def get_4_random_dj_ids():
    """For "Who has been on the air the longest?"
    and "Who has the most shows?" questions."""
    
    return sample(get_all_dj_ids(), k=4)


def get_playlists_by_dj(dj_id):
    """Shows by a DJ."""

    return Playlist.query.filter(Playlist.dj_id == dj_id).all()


def get_random_dj_id():
    """Select a random dj_id from the pile."""

    unique_dj_ids, _ = get_all_dj_ids()
    return choice(unique_dj_ids)

def get_all_playlists_by_dj_id(dj_id=None):
    """Get the body of work for a dj_id. If not specified, returns a random one."""

    if not dj_id:
        dj_id = get_random_dj_id()
    air_name = dj_id_to_airname(dj_id=dj_id)
    their_playlists = get_playlists_by_dj(dj_id=dj_id)
    count_playlists = len(their_playlists)
    return air_name, count_playlists, their_playlists

def dj_id_to_airname(dj_id):
    """Translate dj_id for computers into air_name for humans."""

    return Playlist.query.filter(Playlist.dj_id == dj_id).first().air_name

def a_dj_is_born(dj_id):
    """When did dj_id log their first show?"""

    first_playlist = db.session.query(Playlist).filter(
        Playlist.dj_id == dj_id).order_by(Playlist.start_time).first()
    air_name = dj_id_to_airname(dj_id)
    return air_name, first_playlist.start_time, f"{air_name}'s first show was on {first_playlist.start_time}."

def get_air_names_by_age():
    air_names_by_age = OrderedDict()
    for playlist in db.session.query(Playlist).order_by(Playlist.start_time).all():
        if playlist.dj_id not in air_names_by_age and (
            playlist.air_name) and "KFJC" not in playlist.air_name:
                air_names_by_age[playlist.dj_id] = [playlist.air_name, playlist.start_time]
    return air_names_by_age

def get_air_names_by_show_count():
    air_names_by_show_count = []
    for dj_id in get_all_dj_ids():
        air_name, count_playlists, _their_playlists = get_all_playlists_by_dj_id(dj_id=dj_id)
        if air_name and "KFJC" not in air_name:
            air_names_by_show_count.append([air_name, count_playlists])

    air_names_by_show_count = common.sort_nested_lists(
        a_list_of_lists=air_names_by_show_count, by_key=1, reverse=False)
    return air_names_by_show_count

def all_dj_birthdays():
    """A sanity check for a_dj_is_born()."""
    
    birthdays = []
    for dj_id in get_all_dj_ids():
        #if int(dj_id) > 0:
        _, _, sentence  = a_dj_is_born(dj_id)
        birthdays.append(sentence)

    for j in birthdays:
        print(j)

if __name__ == '__main__':
    """Will connect you to the database when you run playlists.py interactively"""
    from server import app
    connect_to_db(app)
