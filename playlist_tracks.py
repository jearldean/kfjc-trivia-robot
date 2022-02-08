"""Playlist Track operations for KFJC Trivia Robot."""

from random import randint  #, choice

from model import db, connect_to_db, PlaylistTrack
import common


def create_playlist_track(
    kfjc_playlist_id, indx, kfjc_album_id, album_title, artist, 
    track_title, time_played):
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


def get_playlist_tracks(limit_to=10):
    """Get all playlist_tracks up to limit_to. There are ~2.5mil rows in this table."""

    return PlaylistTrack.query.limit(limit_to).all()

"""
def get_playlist_tracks_by_user_id(playlist_id):
    return PlaylistTrack.query.filter(
        PlaylistTrack.playlist_id == playlist_id).all()
        

def get_playlist_track_by_playlist_id_and_indx(playlist_id, indx):
    ""Get a playlist_track by playlist_id and indx.
    
    !!!The primary key is not the station's playlist_id.!!!""

    return PlaylistTrack.query.filter(
        PlaylistTrack.playlist_id == playlist_id,
        PlaylistTrack.indx == indx).first()


def get_random_playlist_track():
    ""Returns one track from all songs played since 1995-09-19 22:00:00.""

    id_ = randint(1, common.get_count(PlaylistTrack.id_))
    random_playlist_track = PlaylistTrack.query.get(id_)

    if random_playlist_track.artist in ['NULL', ""] and (
            random_playlist_track.track_title in ['NULL', ""]) and (
                random_playlist_track.album_title in ['NULL', ""]):
        # What you got there is a blank line. Pick again.
        return get_random_playlist_track()
    else:
        return random_playlist_track"""


def count_playlist_tracks():
    """Counts rows in the table."""
    
    return common.get_count(PlaylistTrack.id_, unique=False)

if __name__ == '__main__':
    """Will connect you to the database when you run playlist_tracks.py interactively"""
    from server import app
    connect_to_db(app)
