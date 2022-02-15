"""Track operations for KFJC Trivia Robot."""

from model import db, connect_to_db, Track


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


def album_tracks(kfjc_album_id):
    """Search and return tracks from an album in play order."""

    compilation_determination = (
        f""" SELECT artist
        FROM tracks 
        WHERE kfjc_album_id = {kfjc_album_id}
        ORDER BY indx """)

    artists = set([row[0] for row in db.session.execute(compilation_determination)])
    include_artist = ", artist " if len(artists) != 1 else ""

    album_tracks = (
        f""" SELECT indx, title {include_artist}
        FROM tracks 
        WHERE kfjc_album_id = {kfjc_album_id}
        ORDER BY indx """)

    return db.session.execute(album_tracks)
    

if __name__ == '__main__':
    """Will connect you to the database when you run tracks.py interactively"""
    from server import app
    connect_to_db(app)
