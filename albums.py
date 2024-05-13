"""Album operations for KFJC Trivia Robot."""

from model import db, connect_to_db, Album


def create_album(
        kfjc_album_id: int, artist: str, title: str,
        is_collection: bool) -> Album:
    """Create and return a new album."""

    album = Album(
        kfjc_album_id=kfjc_album_id,
        artist=artist,
        title=title,
        is_collection=is_collection)

    db.session.add(album)
    # Don't forget to call model.db.session.commit() when done adding items.

    return album


def get_album_by_id(kfjc_album_id: int) -> Album:
    """Return an album by primary key."""

    return Album.query.get(kfjc_album_id)


if __name__ == '__main__':
    """Will connect you to the database when you run albums.py interactively"""
    from server import app

    connect_to_db(app)
