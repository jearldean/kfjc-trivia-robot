"""Album operations for KFJC Trivia Robot."""

from random import randint

from model import db, connect_to_db, Album
import tracks
import collection_tracks
import common


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


def lookup_tracks(album_instance):
    """Get all tracks from a particular album."""

    if album_instance.is_collection:
        return collection_tracks.get_collection_tracks_on_album_id(album_id=album_instance.album_id)
    else:
        return tracks.get_tracks_on_album_id(album_id=album_instance.album_id)


def lookup_track_names(album_instance):
    """Returns a list of Track.titles."""

    tracks = lookup_tracks(album_instance)
    track_names = []
    for dd in tracks:
        track_names.append(dd.title)
    return track_names


def get_albums_by_title(title):
    """Get all albums of a particular title."""

    return Album.query.filter(Album.title == title).all()


def get_albums_with_word_in_title(word):
    """Get albums with a word in the title."""

    return Album.query.filter(Album.title.ilike("%"+word+"%")).order_by(
        Album.album_id).all()


def get_random_album():
    """Returns one album from the library."""

    id_ = randint(1, count_albums())
    return Album.query.get(id_)


def count_albums():
    """How many albums are in our record library?"""

    return common.get_count(Album.id_, unique=False)


def total_tracks():
    """Count the tracks in the tracks library and collections library."""

    return tracks.count_tracks() + collection_tracks.count_collection_tracks()


if __name__ == '__main__':
    """Will connect you to the database when you run albums.py interactively"""
    from server import app
    connect_to_db(app)
