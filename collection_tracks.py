"""Collection Track operations for KFJC Trivia Robot."""

from random import randint

from model import db, connect_to_db, CollectionTrack
import common


def create_collection_track(album_id, title, artist, indx, clean):
    """Create and return a new collection_track."""

    collection_track = CollectionTrack(album_id=album_id, title=title, 
        artist=artist, indx=indx, clean=clean)

    db.session.add(collection_track)
    # Don't forget to call model.db.session.commit() when done adding items.

    return collection_track


def get_collection_tracks(limit_to=10):
    """Get all get_collection_tracks up to limit_to. There are ~125k rows in this table."""

    return CollectionTrack.query.limit(limit_to).all()


def get_collection_tracks_on_album_id(album_id):
    """Get all tracks on a particular collection album."""

    return CollectionTrack.query.filter(CollectionTrack.album_id == album_id).order_by(
        CollectionTrack.indx).all()


def get_collection_tracks_with_word_in_title(word):
    """Get collection tracks with a word in the title."""

    return CollectionTrack.query.filter(CollectionTrack.title.ilike("%"+word+"%")).order_by(
        CollectionTrack.album_id).all()


def who_is_on_this_album(album_id):
    """Returns list of artists on a collection album."""

    selection = CollectionTrack.query.with_entities(CollectionTrack.artist).filter(
        CollectionTrack.album_id == album_id).order_by(CollectionTrack.indx).all()
    
    values = [value[0] for value in selection]

    return values


def get_random_collection_track():
    """Returns one track from the collection track library."""

    id_ = randint(1, count_collection_tracks())
    return CollectionTrack.query.get(id_)


def count_collection_tracks():
    """How many collection tracks are in our record library?"""

    return common.get_count(CollectionTrack.id_, unique=False)


def count_track_titles():
    """How many unique collection song titles are in our record library?"""

    return common.get_count(CollectionTrack.title, unique=True)


if __name__ == '__main__':
    """Will connect you to the database when you run collection_tracks.py interactively"""
    from server import app
    connect_to_db(app)
