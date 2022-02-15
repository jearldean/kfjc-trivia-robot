"""Playlist operations for KFJC Trivia Robot."""

from model import db, connect_to_db, Playlist

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


def dj_stats(order_by = None, reverse = False):
    """Search and return air_name, first_show, last_show and show_count for all DJs 
    achieving MIN_SHOW_COUNT.
    """
    if order_by in ['air_name']:
        sql_variable = "dj_id_to_air_name.air_name"
    elif order_by in ['first_show']:
        sql_variable = "first_last_count.FIRSTSHOW"
    elif order_by in ['last_show']:
        sql_variable = "first_last_count.LASTSHOW"
    elif order_by in ['show_count']:
        sql_variable = "first_last_count.SHOWCOUNT"
    elif order_by in ['dj_id']:
        sql_variable = "first_last_count.dj_id"
    else:
        sql_variable = "first_last_count.SHOWCOUNT"
    if reverse:
        sql_variable += " DESC"

    prolific_djs = (
        f"""SELECT dj_id 
        FROM playlists 
        GROUP by dj_id 
        HAVING count(dj_id) > {MIN_SHOW_COUNT} """)
    first_last_count = (
        f"""SELECT dj_id, min(start_time) as FIRSTSHOW, max(start_time) as LASTSHOW, 
        count(dj_id) as SHOWCOUNT 
        FROM playlists 
        GROUP by dj_id 
        HAVING dj_id in ({prolific_djs}) """)
    dj_id_to_air_name = (
        f"""SELECT dj_id, air_name 
        FROM ( 
            SELECT *, ROW_NUMBER() OVER (PARTITION BY dj_id ORDER BY dj_id) rn 
            FROM playlists) q 
        WHERE rn = 1 
        AND dj_id NOT IN (431, -1) 
        AND air_name NOT LIKE '%KFJC%' 
        AND air_name NOT LIKE '%rebroadcast%' """)
    dj_stats = (
        f"""SELECT dj_id_to_air_name.air_name, first_last_count.dj_id, 
        first_last_count.SHOWCOUNT, first_last_count.FIRSTSHOW, first_last_count.LASTSHOW 
        FROM ({first_last_count}) first_last_count 
        LEFT JOIN ({dj_id_to_air_name}) dj_id_to_air_name 
        ON (first_last_count.dj_id = dj_id_to_air_name.dj_id) 
        ORDER BY {sql_variable} """)

    return db.session.execute(dj_stats)


if __name__ == '__main__':
    """Will connect you to the database when you run playlists.py interactively"""
    from server import app
    connect_to_db(app)
