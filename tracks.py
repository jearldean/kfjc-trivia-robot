"""Track operations for KFJC Trivia Robot."""

from random import randint

from model import db, connect_to_db, Track, Album
import common


def create_track(album_id, title, indx, clean):
    """Create and return a new track."""

    track = Track(album_id=album_id, title=title, indx=indx, clean=clean)

    db.session.add(track)
    # Don't forget to call model.db.session.commit() when done adding items.

    return track


def get_tracks(limit_to=10):
    """Get all tracks up to limit_to. There are ~700k rows in this table."""

    return Track.query.limit(limit_to).all()

    
def get_tracks_between_2_track_ids(first, last):
    """Get all tracks between."""

    return Track.query.filter(Track.id_.between(first, last)).all()


def get_track_by_id(track_id):
    """Get a track by track_id."""

    return Track.query.get(track_id)


def get_tracks_on_album_id(album_id):
    """Get all tracks on a particular album."""

    return Track.query.filter(Track.album_id == album_id).order_by(Track.indx).all()

     
def get_tracks_with_word_in_title(word):
    """Get tracks with a word in the title."""

    return Track.query.filter(Track.title.contains(word)).order_by(Track.album_id).all()


def get_album_for_track(track_id):
    """Get album_instance for a track_id."""

    return Album.query.filter(Track.album_id == Album.album_id, Track.id_ == track_id).first()


def get_artist_for_track_id(track_id):
    """Not needed on collections. Lookup the album artist for a track_id."""

    album_instance = get_album_for_track(track_id)

    return album_instance.artist


def get_artist_for_track_instance(track_instance):
    """Not needed on collections. Lookup the album artist for a track_id."""

    album_instance = get_album_for_track(track_instance.id_)

    return album_instance.artist


def get_tracks_with_word_in_title(word):
    """Get tracks with a word in the title."""

    return Track.query.filter(Track.title.ilike("%"+word+"%")).order_by(
        Track.album_id).all()


def get_random_track():
    """Returns one track from the non-collection library."""

    id_ = randint(1, count_tracks())
    return Track.query.get(id_)


def count_tracks():
    """How many non-collection tracks are in our record library?"""

    return common.get_count(Track.id_, unique=False)


def count_track_titles():
    """How many unique song titles are in our record library?"""

    return common.get_count(Track.title, unique=True)


if __name__ == '__main__':
    """Will connect you to the database when you run tracks.py interactively"""
    from server import app
    connect_to_db(app)
