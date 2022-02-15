"""Playlist Track operations for KFJC Trivia Robot."""

from sqlalchemy import func, text

from model import db, connect_to_db, PlaylistTrack


def create_playlist_track(
    kfjc_playlist_id, indx, kfjc_album_id, album_title, artist, track_title,
    time_played):
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


def djs_favorite(dj_id, artist=None, album=None, track=None, min_plays=5):
    """Search and return a DJ's favorite artist, album or track."""

    if artist:
        sql_variable = "artist"
    elif album:
        sql_variable = "album_title"
    elif track:
        sql_variable = "track_title"
    else:
        return  # You need to put in one of the three.

    djs_playlists = (
        f"""SELECT kfjc_playlist_id 
        FROM playlists 
        WHERE dj_id = {dj_id} """)
    djs_favorite = (
        f"""SELECT {sql_variable}, count({sql_variable}) 
        FROM playlist_tracks 
        WHERE kfjc_playlist_id in ({djs_playlists}) 
        GROUP BY {sql_variable} 
        HAVING count({sql_variable}) > {min_plays} 
        ORDER BY count({sql_variable}) DESC """)

    return db.session.execute(djs_favorite)


def last_time_played(artist=None, album=None, track=None):
    """Search and return the last time any DJ played an artist, album or track."""

    if artist:
        sql_variable = "artist"
        search_variable = artist.lower()
    elif album:
        sql_variable = "album_title"
        search_variable = album.lower()
    elif track:
        sql_variable = "track_title"
        search_variable = track.lower()
    else:
        return  # You need to put in one of the three.

    who_played_it_when = (
        f""" SELECT p.air_name, pt.artist, pt.album_title, pt.track_title, pt.time_played 
        FROM playlists as p 
        INNER JOIN playlist_tracks as pt 
        ON (p.kfjc_playlist_id = pt.kfjc_playlist_id) 
        WHERE LOWER(pt.{sql_variable}) LIKE '%{search_variable}%' 
        AND pt.time_played IS NOT NULL 
        ORDER BY pt.time_played """)

    return db.session.execute(who_played_it_when)


def top_n(start_date, end_date, top=10, artist=None, album=None, track=None):
    """Search and return the KFJC Top10, Top40 or Top* by artist, album or track for any time period.
    
    Playlist time_played is only really reliable since 2012."""

    if artist:
        sql_variable = "artist"
        group_by = "artist, album_title, track_title"
    elif album:
        sql_variable = "album_title"
        group_by = "album_title, artist, track_title"
    elif track:
        sql_variable = "track_title"
        group_by = "track_title, artist, album_title"
    else:  # Just use track, then.
        sql_variable = "track_title"
        group_by = "track_title, artist, album_title"

    top_n_search = text(
        f""" SELECT count({sql_variable}), {group_by}
        FROM playlist_tracks 
        WHERE time_played >= date('{start_date}') 
        AND time_played <= date('{end_date}') 
        GROUP BY {group_by}
        ORDER BY count({sql_variable}) DESC 
        LIMIT {top} """)

    return db.session.execute(top_n_search)


if __name__ == '__main__':
    """Will connect you to the database when you run playlist_tracks.py interactively"""
    from server import app
    connect_to_db(app)
