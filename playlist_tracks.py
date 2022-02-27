"""Playlist Track operations for KFJC Trivia Robot."""

from sqlalchemy import text, func, select, exc

from model import db, connect_to_db, PlaylistTrack
import common

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

# -=-=-=-=-=-=-=-=-=-=-=- DJ Favorites -=-=-=-=-=-=-=-=-=-=-=-

def get_favorite_artists(dj_id, reverse=True, min_plays=5):
    """Search and return a list of DJ's favorite artists."""
    return djs_favorite(dj_id=dj_id, sql_variable="artist", reverse=reverse, min_plays=min_plays)

def get_favorite_albums(dj_id, reverse=True, min_plays=5):
    """Search and return a list of DJ's favorite albums."""
    return djs_favorite(dj_id=dj_id, sql_variable="album_title", reverse=reverse, min_plays=min_plays)

def get_favorite_tracks(dj_id, reverse=True, min_plays=5):
    """Search and return a list of DJ's favorite tracks."""
    return djs_favorite(dj_id=dj_id, sql_variable="track_title", reverse=reverse, min_plays=min_plays)

def djs_favorite(dj_id, sql_variable, reverse=True, min_plays=5):
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
        GROUP BY {sql_variable} 
        HAVING count({sql_variable}) > {min_plays} 
        ORDER BY count({sql_variable}) {reverse_it} """)

    reply = db.session.execute(djs_favorite)
    reply_named_tuple = common.convert_dicts_to_named_tuples(reply)
    return reply_named_tuple

# -=-=-=-=-=-=-=-=-=-=-=- Top10, Top10, Most Plays -=-=-=-=-=-=-=-=-=-=-=-

def get_top10_artists(start_date, end_date, n=10):
    """Going to make it a discoverable feature in REST API that they can ask for the
    top 40, 29 or 123 artists if they so desire. *** """

    return get_top_plays(
        start_date=start_date, end_date=end_date, 
        sql_variable="artist", group_by="artist, album_title, track_title", n=n)

def get_top10_albums(start_date, end_date, n=10):
    """TODO"""
    return get_top_plays(
        start_date=start_date, end_date=end_date, 
        sql_variable="album_title", group_by="album_title, artist, track_title", n=n)

def get_top10_tracks(start_date, end_date, n=10):
    """TODO"""
    return get_top_plays(
        start_date=start_date, end_date=end_date, 
        sql_variable="track_title", group_by="track_title, artist, album_title", n=n)

def get_top_plays(start_date, end_date, sql_variable, group_by, n=10):
    """Get the top plays between any two dates.***"""

    top_n = text(
        f""" SELECT count({sql_variable}) as plays, {group_by}
        FROM playlist_tracks 
        WHERE time_played >= date('{start_date}') 
        AND time_played <= date('{end_date}') 
        GROUP BY {group_by}
        ORDER BY count({sql_variable}) DESC 
        LIMIT {n} """)

    reply = db.session.execute(top_n)
    reply_named_tuple = common.convert_dicts_to_named_tuples(reply)
    return reply_named_tuple

# -=-=-=-=-=-=-=-=-=-=-=- When is the last time someone played _ ? -=-=-=-=-=-=-=-=-=-=-=-

def get_a_random_artist(min_appearances=3):
    """"""
    return random_library_pick(pick_type='artist', min_appearances=min_appearances)

def get_a_random_album(min_appearances=3):
    """"""
    return random_library_pick(pick_type='album_title', min_appearances=min_appearances)

def get_a_random_track(min_appearances=3):
    """"""
    return random_library_pick(pick_type='track_title', min_appearances=min_appearances)

def all_random_library_picks(pick_type='track_title', min_appearances=3):
    """"""
    if pick_type in ['artist', 'Artist']:
        library_category = PlaylistTrack.artist
        pick_type = 'artist'
    elif pick_type in ['album', 'Album', 'album_title']:
        library_category = PlaylistTrack.album_title
        pick_type = 'album'
    else:  # Just give 'em a track, I guess.
        library_category = PlaylistTrack.track_title
        pick_type = 'track'

    all_playlist_tracks_random = None
    while not all_playlist_tracks_random:
        try:
            all_playlist_tracks_random = db.session.query(library_category).filter(
                PlaylistTrack.time_played.isnot(None)).group_by(
                library_category).having(func.count(library_category) > min_appearances).order_by(
                    func.random()).all()
        except exc.ProgrammingError:
            continue  # Pick again if there's a problem.
        except exc.InternalError:
            continue  # Pick again if there's a problem.

    reply_named_tuple = common.convert_dicts_to_named_tuples(all_playlist_tracks_random)
    return reply_named_tuple

def random_library_pick(pick_type='track_title', min_appearances=3):
    """TODO"""
    if pick_type in ['artist', 'Artist']:
        library_category = PlaylistTrack.artist
        pick_type = 'artist'
    elif pick_type in ['album', 'Album', 'album_title']:
        library_category = PlaylistTrack.album_title
        pick_type = 'album'
    else:  # Just give 'em a track, I guess.
        library_category = PlaylistTrack.track_title
        pick_type = 'track'

    random_pick = None
    while not random_pick:
        try:
            one_playlist_item = db.session.query(library_category).group_by(
                library_category).having(func.count(library_category) > min_appearances).order_by(
                    func.random()).first()
            if pick_type == 'artist':
                random_pick = one_playlist_item.artist
            elif pick_type == 'album':
                random_pick = one_playlist_item.album_title
            else:  # elif pick_type == 'track':
                random_pick = one_playlist_item.track_title
        except exc.ProgrammingError:
            continue  # Pick again if there's a problem.
        except exc.InternalError:
            continue  # Pick again if there's a problem.

    reply_named_tuple = common.convert_dicts_to_named_tuples(random_pick)
    return reply_named_tuple

""" ***
Keep in mind: playlist_tracks.time_played has only been collected since 2011 but,
for earlier playlist_tracks, we are borrowing the playlist.start_time as the 
playlist_tracks.time_played so we can make more questions.
"""

def get_last_play_of_artist(artist, reverse=False):
    """Search and return the last plays of an artist.***"""

    return last_time_played(search_column_name="artist", search_for_item=artist, reverse=reverse)

def get_last_play_of_album(album, reverse=False):
    """Search and return the last plays of an album.***"""

    return last_time_played(search_column_name="album_title", search_for_item=album, reverse=reverse)

def get_last_play_of_track(track, reverse=False):
    """Search and return the last plays of a track.***"""

    return last_time_played(search_column_name="track_title", search_for_item=track, reverse=reverse)

def last_time_played(search_column_name, search_for_item, reverse=False):
    """Search and return the last time any DJ played an artist, album or track."""

    reverse_it = "DESC" if reverse else ""
    who_played_it_when = (
        f""" SELECT p.air_name, pt.artist, pt.album_title, pt.track_title, pt.time_played 
        FROM playlists as p 
        INNER JOIN playlist_tracks as pt 
        ON (p.kfjc_playlist_id = pt.kfjc_playlist_id) 
        WHERE LOWER(pt.{search_column_name}) LIKE LOWER('%{search_for_item}%') 
        AND pt.time_played IS NOT NULL 
        ORDER BY pt.time_played {reverse_it} """)

    reply_named_tuple = common.convert_dicts_to_named_tuples(who_played_it_when)
    return reply_named_tuple

# -=-=-=-=-=-=-=-=-=-=-=- Get stats for greeting statement -=-=-=-=-=-=-=-=-=-=-=-

def how_many_tracks():
    """Count all playlist_tracks for the homepage statement."""
    return common.get_count(PlaylistTrack.id_)

if __name__ == '__main__':
    """Will connect you to the database when you run playlist_tracks.py interactively"""
    from server import app
    connect_to_db(app)
