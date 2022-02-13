"""Playlist operations for KFJC Trivia Robot."""

from itertools import groupby
from random import choice, sample
from collections import OrderedDict

from model import db, connect_to_db, Playlist
from sqlalchemy.sql.expression import func, distinct
import common

MIN_SHOW_COUNT = 40
# Might do tuning and raise this... The first 14 playlists by any DJ are training missions
# and more playlists are required to become a DJ relevant enough to ask questions on.


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
    


def get_playlists_by_dj(dj_id):
    """Shows by a DJ."""

    return Playlist.query.filter(Playlist.dj_id == dj_id).all()


def get_all_playlists_by_dj_id(dj_id=None):
    """Get the body of work for a dj_id. If not specified, returns a random one."""

    their_playlists = get_playlists_by_dj(dj_id=dj_id)
    count_playlists = len(their_playlists)

    first_show = Playlist.query.order_by(Playlist.start_time).filter(
        Playlist.dj_id == dj_id).limit(1).first().start_time
    last_show = Playlist.query.order_by(Playlist.start_time.desc()).filter(
        Playlist.dj_id == dj_id).limit(1).first().start_time

    return count_playlists, first_show, last_show, their_playlists


def dj_stats():
    prolific_djs = f"""SELECT dj_id 
                        FROM playlists 
                        GROUP by dj_id 
                        HAVING count(dj_id) > {MIN_SHOW_COUNT} """
    first_last_count = f"""SELECT dj_id, min(start_time) as FIRSTSHOW, max(start_time) as LASTSHOW, count(dj_id) as SHOWCOUNT 
                        FROM playlists 
                        GROUP by dj_id 
                        HAVING dj_id in ({prolific_djs}) """
    dj_id_to_air_name = f"""SELECT dj_id, air_name 
                        FROM (
                            SELECT *, ROW_NUMBER() OVER (PARTITION BY dj_id ORDER BY dj_id) rn
                            FROM playlists) q
                        WHERE rn = 1
                        AND dj_id != 431
                        AND dj_id != -1
                        AND air_name NOT LIKE '%KFJC%'
                        AND air_name NOT LIKE '%rebroadcast%'
                        ORDER BY dj_id"""
    air_names_by_firstshow = f"""SELECT dj_id_to_air_name.air_name, first_last_count.dj_id, first_last_count.SHOWCOUNT, first_last_count.LASTSHOW, first_last_count.FIRSTSHOW
                        FROM ({first_last_count}) first_last_count
                        LEFT JOIN ({dj_id_to_air_name}) dj_id_to_air_name
                        ON (first_last_count.dj_id = dj_id_to_air_name.dj_id)
                        WHERE first_last_count.dj_id != 431
                        AND first_last_count.dj_id != -1
                        ORDER BY first_last_count.FIRSTSHOW
                        """
    result = db.session.execute(air_names_by_firstshow)
    return result


if __name__ == '__main__':
    """Will connect you to the database when you run playlists.py interactively"""
    from server import app
    connect_to_db(app)
