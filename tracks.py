"""Track operations for KFJC Trivia Robot."""

from model import db, connect_to_db, Track
import common

def create_track(kfjc_album_id, artist, title, indx):
    """Create and return a new track."""

    track = Track(
        kfjc_album_id=kfjc_album_id, 
        artist=artist,
        title=title,
        indx=indx)

    db.session.add(track)
    # Don't forget to call model.db.session.commit() when done adding items.

    return track

# -=-=-=-=-=-=-=-=-=-=-=- Tracks on an Album -=-=-=-=-=-=-=-=-=-=-=-

def get_tracks_by_kfjc_album_id(kfjc_album_id):
    """Get artist, album title and track from an album."""

    tracks = Track.query.filter(Track.kfjc_album_id == kfjc_album_id).all()
    reply_named_tuple = common.convert_dicts_to_named_tuples(tracks)
    return reply_named_tuple


if __name__ == '__main__':
    """Will connect you to the database when you run tracks.py interactively"""
    from server import app
    connect_to_db(app)
