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


def get_albums():
    """Get all albums."""

    return Album.query.all()



def get_albums_by_kfjc_album_id(kfjc_album_id):
    """Get an album from the kfjc_album_id."""

    return Album.query.filter(Album.kfjc_album_id == kfjc_album_id).first()



def get_albums_by_artist(artist):
    """Get all albums from a particular artist."""

    return Album.query.filter(Album.artist == artist).all()

"""
def lookup_track_names(album_instance):
    ""Returns a list of Track.titles.""

    tracks = lookup_tracks(album_instance)
    track_names = []
    for dd in tracks:
        track_names.append(dd.title)
    return track_names


def get_albums_by_title(title):
    ""Get all albums of a particular title.""

    return Album.query.filter(Album.title == title).all()


def get_albums_with_word_in_title(word):
    ""Get albums with a word in the title.""

    return Album.query.filter(Album.title.ilike("%"+word+"%")).order_by(
        Album.album_id).all()


def get_random_album():
    ""Returns one album from the library.""

    id_ = randint(1, count_albums())
    return Album.query.get(id_)


def count_albums():
    ""How many albums are in our record library?""

    return common.get_count(Album.id_, unique=False)


def total_tracks():
    ""Count the tracks in the tracks library and collections library.""

    return tracks.count_tracks() + collection_tracks.count_collection_tracks()"""


if __name__ == '__main__':
    """Will connect you to the database when you run albums.py interactively"""
    from server import app
    connect_to_db(app)
