"""Track operations for KFJC Trivia Robot."""

from model import db, connect_to_db, Track, Album


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
    """Get artist, album title and track from a kfjc_album_id."""

    album = Album.query.get(kfjc_album_id)
    return get_tracks(album)

def get_tracks(album):
    """Get artist, album title and track from a kfjc_album_id."""

    unpacked_tracks = []
    for track in album.tracks:  # Using the relationship we made.
        if track.artist:
            unpacked_tracks.append([track.indx, track.artist, album.title, track.title])
        else:
            # Try the albums table for the Artist:
            unpacked_tracks.append([track.indx, album.artist, album.title, track.title])
    
    return unpacked_tracks


if __name__ == '__main__':
    """Will connect you to the database when you run tracks.py interactively"""
    from server import app
    connect_to_db(app)
