"""Playlist operations for KFJC Trivia Robot."""

from sqlalchemy import func

from model import db, connect_to_db, Playlist
import common

MIN_SHOW_COUNT = 14
# A DJ is born when they complete one training excercise and 13 grave shifts.

ADMINISTRATIVE_DJ_IDS = (
    1, 58, 57, -1, 434, 445, 191, 164, 105, 433,
    104, 139, 120, 432, 431, 123, 122, 114, 424, 423, 140)
# TODO use the 'administrative' boolean column you made.


def create_playlist(kfjc_playlist_id, dj_id, air_name, start_time, end_time):
    """Create and return a new playlist."""

    playlist = Playlist(
        kfjc_playlist_id=kfjc_playlist_id,
        dj_id=dj_id,
        air_name=air_name,
        start_time=start_time,
        end_time=end_time)

    db.session.add(playlist)
    # Don't forget to call model.db.session.commit() when done adding items.

    return playlist


def get_playlist_by_id(kfjc_playlist_id):
    """Return an album by primary key."""

    return Playlist.query.get(kfjc_playlist_id)

# -=-=-=-=-=-=-=-=-=-=-=- DJ Stats -=-=-=-=-=-=-=-=-=-=-=-


def get_djs_by_dj_id(reverse=False):
    """Return DJ Stats in order of dj_id."""
    return dj_stats(order_by_column="first_last_count.dj_id", reverse=reverse)


def get_djs_alphabetically(reverse=False):
    """Return DJ Stats in alphabetical order of air_name."""
    return dj_stats(
        order_by_column="UPPER(dj_id_to_air_name.air_name)", reverse=reverse)


def get_djs_by_first_show(reverse=False):
    """Return DJ Stats in order of their first show."""
    return dj_stats(
        order_by_column="first_last_count.FIRSTSHOW", reverse=reverse)


def get_djs_by_last_show(reverse=False):
    """Return DJ Stats in order of their last show."""
    return dj_stats(
        order_by_column="first_last_count.LASTSHOW", reverse=reverse)


def get_djs_by_show_count(reverse=False):
    """Return DJ Stats in order of their total shows."""
    return dj_stats(
        order_by_column="first_last_count.SHOWCOUNT",
        reverse=reverse)


def dj_stats(order_by_column, reverse=False):
    """Everything there is to know about DJs: air_name,
    dj_id, showcount, firstshow and lastshow."""
    reverse_it = "DESC" if reverse else ""
    prolific_djs = (
        f"""SELECT dj_id
        FROM playlists
        GROUP by dj_id
        HAVING count(dj_id) > {MIN_SHOW_COUNT} """)
    first_last_count = (
        f"""SELECT dj_id, min(start_time) as FIRSTSHOW,
        max(start_time) as LASTSHOW,
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
        AND dj_id NOT IN {ADMINISTRATIVE_DJ_IDS}
        AND air_name NOT LIKE '%KFJC%' """)
    # TODO PUT BACK  AND administrative is False
    dj_stats = (
        f"""SELECT dj_id_to_air_name.air_name, first_last_count.dj_id,
        first_last_count.SHOWCOUNT as showcount,
        first_last_count.FIRSTSHOW as firstshow,
        first_last_count.LASTSHOW as lastshow
        FROM ({first_last_count}) first_last_count
        LEFT JOIN ({dj_id_to_air_name}) dj_id_to_air_name
        ON (first_last_count.dj_id = dj_id_to_air_name.dj_id)
        WHERE dj_id_to_air_name.dj_id NOT IN {ADMINISTRATIVE_DJ_IDS}
        ORDER BY {order_by_column} {reverse_it} """)
    # TODO PUT BACK  AND administrative is False

    results = db.session.execute(dj_stats)
    reply_named_tuple = (
        common.convert_list_o_dicts_to_list_o_named_tuples(results))
    return reply_named_tuple

# -=-=-=-=-=-=-=-=- Get stats for greeting statement -=-=-=-=-=-=-=-=-


def first_show_last_show():
    """Get the head and tail of the Playlist.start_time."""
    return common.get_ages(Playlist.start_time)


def get_dj_ids_and_show_counts():
    """Return a list of named tuples of dj_ids and their showcount."""
    result_tuples = db.session.query(
        func.count(Playlist.dj_id).label('showcount'),
        Playlist.dj_id).group_by(
        Playlist.dj_id).having(
            func.count(Playlist.dj_id) > MIN_SHOW_COUNT).all()
    return common.convert_list_o_dicts_to_list_o_named_tuples(
        list_of_dicts=result_tuples)
    # [GenericDict(showcount=26, dj_id=53), ...]


def get_all_dj_ids():
    return [x.dj_id for x in get_dj_ids_and_show_counts()]


def how_many_djs():
    """Count all DJs for the homepage statement."""
    return len(get_dj_ids_and_show_counts())


def get_dj_id(air_name):
    """Get dj_id from air_name."""
    return Playlist.query.filter(Playlist.air_name == air_name).first().dj_id


def how_many_shows():
    """Count all playlists for the homepage statement."""
    return common.get_count(Playlist.kfjc_playlist_id)


if __name__ == '__main__':
    """Will connect you to the database when you run
    playlists.py interactively"""
    from server import app
    connect_to_db(app)
