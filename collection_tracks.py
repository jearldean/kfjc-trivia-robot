"""Collection Track operations for KFJC Trivia Robot."""

from model import db, connect_to_db, CollectionTrack


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

    return CollectionTrack.query.filter(CollectionTrack.title.contains(word)).order_by(
        CollectionTrack.album_id).all()


def who_is_on_this_album(album_id):

    selection = CollectionTrack.query.with_entities(CollectionTrack.artist).filter(
        CollectionTrack.album_id == album_id).order_by(CollectionTrack.indx).all()
    
    values = [value[0] for value in selection]

    return values


if __name__ == '__main__':
    """Will connect you to the database when you run collection_tracks.py interactively"""
    from server import app
    connect_to_db(app)
