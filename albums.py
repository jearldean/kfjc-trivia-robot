"""Album operations for KFJC Trivia Robot."""

from model import db, connect_to_db, Album


def create_album(album_id, artist, title, is_collection):
    """Create and return a new album."""

    album = Album(album_id=album_id, artist=artist, title=title, is_collection=is_collection)

    db.session.add(album)
    # Don't forget to call model.db.session.commit() when done adding items.

    return album


def get_albums():
    """Get all albums."""

    return Album.query.all()


def get_albums_by_artist(artist):
    """Get all albums from a particular artist."""

    return Album.query.filter(Album.artist == artist).all()


def get_albums_by_title(title):
    """Get all albums of a particular title."""

    return Album.query.filter(Album.title == title).all()



if __name__ == '__main__':
    """Will connect you to the database when you run albums.py interactively"""
    from server import app
    connect_to_db(app)
