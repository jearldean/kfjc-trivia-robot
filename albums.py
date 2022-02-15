"""Album operations for KFJC Trivia Robot."""

from model import db, connect_to_db, Album


def create_album(kfjc_album_id, artist, title):
    """Create and return a new album."""

    album = Album(
        kfjc_album_id=kfjc_album_id,
        artist=artist,
        title=title)

    db.session.add(album)
    # Don't forget to call model.db.session.commit() when done adding items.

    return album


if __name__ == '__main__':
    """Will connect you to the database when you run albums.py interactively"""
    from server import app
    connect_to_db(app)
