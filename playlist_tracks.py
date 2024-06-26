"""Playlist Track operations for KFJC Trivia Robot."""

from sqlalchemy import text, func, exc
from typing import NamedTuple, Union

from model import db, connect_to_db, PlaylistTrack
import djs
import common

LIMITER = 500  # Make sure this agrees with listeners.js.


def create_playlist_track(
        kfjc_playlist_id: int, indx: int, kfjc_album_id: int, album_title: str,
        artist: str, track_title: str, time_played: str) -> PlaylistTrack:
    """Create and return a new playlist_track."""

    playlist_track = PlaylistTrack(
        kfjc_playlist_id=kfjc_playlist_id,
        indx=indx,
        kfjc_album_id=kfjc_album_id,
        album_title=album_title,
        artist=artist,
        track_title=track_title,
        time_played=time_played)

    db.session.add(playlist_track)
    # Don't forget to call model.db.session.commit() when done adding items.

    return playlist_track


def get_playlist_tracks_by_kfjc_playlist_id(
        kfjc_playlist_id: int) -> PlaylistTrack:
    """Return an album by primary key."""

    return PlaylistTrack.query.filter(
        PlaylistTrack.kfjc_playlist_id == kfjc_playlist_id).all()


# -=-=-=-=-=-=-=-=-=-=-=- DJ Favorites -=-=-=-=-=-=-=-=-=-=-=-


def get_favorite_artists(
        dj_id: int, reverse: bool = True, min_plays: int = 5) -> NamedTuple:
    """Search and return a list of DJ's favorite artists."""
    return djs_favorite(
        dj_id=dj_id, sql_variable="artist",
        reverse=reverse, min_plays=min_plays)


def get_favorite_albums(
        dj_id: int, reverse: bool = True, min_plays: int = 5) -> NamedTuple:
    """Search and return a list of DJ's favorite albums."""
    return djs_favorite(
        dj_id=dj_id, sql_variable="album_title",
        reverse=reverse, min_plays=min_plays)


def get_favorite_tracks(
        dj_id: int, reverse: bool = True, min_plays: int = 5) -> NamedTuple:
    """Search and return a list of DJ's favorite tracks."""
    return djs_favorite(
        dj_id=dj_id, sql_variable="track_title",
        reverse=reverse, min_plays=min_plays)


def djs_favorite(
        dj_id: int, sql_variable: str, reverse: bool = True,
        min_plays: int = 5) -> NamedTuple:
    """Search and return a DJ's favorite artists, albums or tracks."""
    reverse_it = "DESC" if reverse else ""
    djs_playlists = (
        f"""SELECT kfjc_playlist_id
        FROM playlists
        WHERE dj_id = {dj_id} """)
    djs_favorite = (
        f"""SELECT {sql_variable}, count({sql_variable}) as plays
        FROM playlist_tracks
        WHERE kfjc_playlist_id in ({djs_playlists})
        AND {sql_variable} != 'None'
        GROUP BY {sql_variable}
        HAVING count({sql_variable}) > {min_plays}
        ORDER BY count({sql_variable}) {reverse_it} """)

    reply = db.session.execute(djs_favorite)
    reply_named_tuple = (
        common.convert_list_o_dicts_to_list_o_named_tuples(reply))
    return reply_named_tuple


def dj_needs_more_shows(dj_id: int) -> str:
    """Sometimes when a DJ has a small body of work, they can't
    meet the minimum number of plays to return any favorite items.

    Will return a status message instead.
    """
    air_name = djs.get_airname_for_dj(dj_id=dj_id)
    warning_will_robinson = (
        f"""Beep! Beep! Not enough data!\nMy databanks show """
        f"""that DJ {air_name} hasn't done enough shows to """
        f"""compute favorites data.""")
    if djs.WHITE_HEART not in air_name:
        # Insensitive to put this on a DJ memorial.
        warning_will_robinson += " Keep listening!"
    return warning_will_robinson


# -=-=-=-=-=-=-=-=-=-=-=- Top10, Top10, Most Plays -=-=-=-=-=-=-=-=-=-=-=-


def get_top10_artists(
        start_date: str, end_date: str, n: int = 10) -> NamedTuple:
    """Top10 artist plays between any 2 dates.

    Going to make it a discoverable feature in REST API that they can ask for
    the top 40, 29 or 123 artists if they so desire. *** """

    return get_top_plays(
        start_date=start_date, end_date=end_date,
        sql_variable="artist",
        group_by="artist, album_title, track_title", n=n)


def get_top10_albums(
        start_date: str, end_date: str, n: int = 10) -> NamedTuple:
    """Top10 album plays between any 2 dates."""
    return get_top_plays(
        start_date=start_date, end_date=end_date,
        sql_variable="album_title",
        group_by="album_title, artist, track_title", n=n)


def get_top10_tracks(
        start_date: str, end_date: str, n: int = 10) -> NamedTuple:
    """Top10 track plays between any 2 dates."""
    return get_top_plays(
        start_date=start_date, end_date=end_date,
        sql_variable="track_title",
        group_by="track_title, artist, album_title", n=n)


def get_top_plays(
        start_date: str, end_date: str, sql_variable: str,
        group_by: str, n: int = 10) -> NamedTuple:
    """Get the top plays between any two dates.***"""

    if start_date > end_date:  # Just flip 'em
        old_start_date = start_date
        old_end_date = end_date
        end_date = old_start_date
        start_date = old_end_date

    top_n = text(
        f""" SELECT count({sql_variable}) as plays, {group_by}
        FROM playlist_tracks
        WHERE time_played >= date('{start_date}')
        AND time_played <= date('{end_date}')
        AND {sql_variable} != 'None'
        GROUP BY {group_by}
        ORDER BY count({sql_variable}) DESC
        LIMIT {n} """)

    reply = db.session.execute(top_n)
    reply_named_tuple = (
        common.convert_list_o_dicts_to_list_o_named_tuples(reply))
    return reply_named_tuple


# -=-=-=-=-=-=-=- When is the last time someone played _ ? -=-=-=-=-=-=-=-


def get_a_random_artist(min_appearances: int = 3) -> str:
    """Return one random artist."""
    return random_library_pick(
        pick_type='artist', min_appearances=min_appearances)


def get_a_random_album(min_appearances: int = 3) -> str:
    """Return one random album_title."""
    return random_library_pick(
        pick_type='album_title', min_appearances=min_appearances)


def get_a_random_kfjc_album_id(min_appearances: int = 3) -> int:
    """Return one random kfjc_album_id."""
    return random_library_pick(
        pick_type='kfjc_album_id', min_appearances=min_appearances)


def get_a_random_track(min_appearances: int = 3) -> str:
    """Return one random track_title."""
    return random_library_pick(
        pick_type='track_title', min_appearances=min_appearances)


def random_library_pick(
        pick_type='track_title', min_appearances: int = 3) -> Union[str, int]:
    """Get one random item from the library."""
    if pick_type in ['artist', 'Artist']:
        library_category = PlaylistTrack.artist
        searcher = library_category
    elif pick_type in ['album', 'Album', 'album_title']:
        library_category = PlaylistTrack.album_title
        searcher = library_category
    elif pick_type in ['kfjc_album_id']:
        library_category = PlaylistTrack.kfjc_album_id
        searcher = PlaylistTrack.album_title
    else:  # Just give 'em a track, I guess.
        library_category = PlaylistTrack.track_title
        searcher = library_category

    try:
        return db.session.query(
            library_category).filter(
            searcher != 'None').group_by(
            library_category).having(
            func.count(
                library_category) > min_appearances).order_by(
            func.random()).first()[0]
    except exc.ProgrammingError:
        # Pick again if there's a problem.
        return
    except exc.InternalError:
        # Pick again if there's a problem.
        return
    except TypeError:  # 'NoneType' object is not subscriptable
        return


""" ***
Keep in mind: playlist_tracks.time_played has only been collected since 2011
but, for earlier playlist_tracks, we are borrowing the playlist.start_time
as the playlist_tracks.time_played so we can make more questions.
"""


def get_last_play_of_artist(artist: str, reverse: bool = False) -> NamedTuple:
    """Search and return the last plays of an artist.***"""

    return last_time_played(
        search_column_name="artist", search_for_item=artist, reverse=reverse)


def get_last_play_of_album(album: str, reverse: bool = False) -> NamedTuple:
    """Search and return the last plays of an album.***"""

    return last_time_played(
        search_column_name="album_title",
        search_for_item=album, reverse=reverse)


def get_last_play_of_track(track: str, reverse: bool = False) -> NamedTuple:
    """Search and return the last plays of a track.***"""

    return last_time_played(
        search_column_name="track_title",
        search_for_item=track, reverse=reverse)


def last_time_played(
        search_column_name: str, search_for_item: str,
        reverse: bool = False) -> NamedTuple:
    """Search and return the last time any DJ played
    an artist, album or track."""

    # LIKE on a bare string is vulnerable to SQL Injection attack;
    # so, neuter their weapons:
    search_for_item = search_for_item.replace(
        "'", " ").replace("dropdb", " ").replace("%", " ").replace(
        "@", " ").replace("-", " ").replace(
        "*", " ").replace("  ", " ").strip()

    # Still, each word should participate in the search:
    search_for_item = search_for_item.replace(" ", "%")

    reverse_it = "DESC" if reverse else ""
    who_played_it_when = (
        f""" SELECT p.dj_id, p.air_name, pt.artist, pt.album_title,
        pt.track_title, pt.time_played
        FROM playlists as p
        INNER JOIN playlist_tracks as pt
        ON (p.kfjc_playlist_id = pt.kfjc_playlist_id)
        WHERE LOWER(pt.{search_column_name}) LIKE LOWER('%{search_for_item}%')
        AND pt.time_played IS NOT NULL
        AND pt.{search_column_name} != 'None'
        ORDER BY pt.time_played {reverse_it}
        LIMIT {LIMITER}""")

    results = db.session.execute(who_played_it_when)
    reply_named_tuple = common.convert_list_o_dicts_to_list_o_named_tuples(
        results)
    return reply_named_tuple


# -=-=-=-=-=-=-=- Get stats for greeting statement -=-=-=-=-=-=-=-


def how_many_tracks() -> int:
    """Count all playlist_tracks for the homepage statement."""
    return common.get_count(PlaylistTrack.id_)


if __name__ == '__main__':
    """Will connect you to the database when you run
    playlist_tracks.py interactively"""
    from server import app

    connect_to_db(app)
