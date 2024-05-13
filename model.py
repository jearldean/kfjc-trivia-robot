"""Models for KFJC Trivia Robot."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy_json import mutable_json_type

db = SQLAlchemy()
# Make sure this agrees with your seed_database.py program:
DATABASE = "trivia"


class User(db.Model):
    """A user."""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(256), unique=True, nullable=False)
    fname = db.Column(db.String(30), unique=False, nullable=True)
    hashed_password = db.Column(db.String, nullable=False)

    # answers = a list of Answer objects

    def __repr__(self):
        spaces = (13 - len(self.fname)) * " "
        return (f"\nU:{self.user_id}\t{self.fname}{spaces}{self.username}")


class Question(db.Model):
    """A question."""

    __tablename__ = 'questions'

    question_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    question_type = db.Column(db.String, nullable=False)
    ask_question = db.Column(db.String, nullable=False)
    present_answer = db.Column(db.String, nullable=False)
    # Tips at https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/
    acceptable_answer = db.Column(db.String, nullable=False)
    display_shuffled_answers = db.Column(
        mutable_json_type(dbtype=JSON, nested=True))
    present_answer_data_headings = db.Column(
        mutable_json_type(dbtype=JSON, nested=True))
    present_answer_data = db.Column(
        mutable_json_type(dbtype=JSON, nested=True))

    # answers = a list of Answer objects

    def __repr__(self):
        spaces = (25 - len(self.question)) * " "
        return (
            f"\nQ:{self.question_id}\t{self.ask_question}"
            f"{spaces}{self.acceptable_answer}")


class Answer(db.Model):
    """A response from a user."""

    __tablename__ = 'answers'

    answer_id = db.Column(
        db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    question_id = db.Column(
        db.Integer, db.ForeignKey("questions.question_id"))
    answer_given = db.Column(db.String, nullable=True)
    answer_correct = db.Column(db.Boolean, nullable=True)
    timestamp = db.Column(db.DateTime)

    question = db.relationship(
        "Question", backref="answers", cascade="all, delete-orphan",
        single_parent=True)
    user = db.relationship(
        "User", backref="answers", cascade="all, delete-orphan",
        single_parent=True)

    def __repr__(self):
        return (
            f"\nA:{self.answer_id}\tU:{self.user_id}\t"
            f"Q:{self.question_id}\t{self.answer_given}\t"
            f"{self.answer_correct}\t{self.timestamp}")


class Dj(db.Model):
    """A DJ from the station."""

    __tablename__ = 'djs'

    dj_id = db.Column(db.Integer, primary_key=True)
    air_name = db.Column(db.String(60), nullable=True)
    administrative = db.Column(db.Boolean)
    silent_mic = db.Column(db.Boolean)

    # playlists = a list of Playlist objects

    def __repr__(self):
        return f"\ndj_id {self.dj_id} belongs to {self.air_name}."


class Playlist(db.Model):
    """A playlist from the station."""

    __tablename__ = 'playlists'

    kfjc_playlist_id = db.Column(db.Integer, primary_key=True)
    dj_id = db.Column(db.Integer, ForeignKey("djs.dj_id"))
    air_name = db.Column(db.String(60), nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)  # '2022-01-19 22:04:31'
    end_time = db.Column(db.DateTime, nullable=True)  # '2022-01-19 22:08:42'
    dj_table_dj_id = db.relationship(
        "Dj", backref="playlists", cascade="all, delete-orphan",
        single_parent=True,
        primaryjoin="Playlist.dj_id == Dj.dj_id")

    def __repr__(self):
        return (
            f"\n{self.kfjc_playlist_id}. {self.air_name} "
            f"on {self.start_time}")


class PlaylistTrack(db.Model):
    """A playlist track from the station."""

    __tablename__ = 'playlist_tracks'

    id_ = db.Column(db.Integer, autoincrement=True, primary_key=True)
    kfjc_playlist_id = db.Column(
        db.Integer, ForeignKey("playlists.kfjc_playlist_id"), nullable=True)
    indx = db.Column(db.Integer, nullable=True)
    kfjc_album_id = db.Column(
        db.Integer, ForeignKey("albums.kfjc_album_id"), nullable=True)
    album_title = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    track_title = db.Column(db.String(100))
    time_played = db.Column(db.DateTime, nullable=True)
    album_kfjc_album_id = db.relationship(
        "Album", backref="playlist_tracks",
        cascade="all, delete-orphan", single_parent=True,
        primaryjoin="PlaylistTrack.kfjc_album_id == Album.kfjc_album_id")
    playlist_kfjc_playlist_id = db.relationship(
        "Playlist", backref="playlist_tracks",
        cascade="all, delete-orphan", single_parent=True,
        primaryjoin=(
            "PlaylistTrack.kfjc_playlist_id == "
            "Playlist.kfjc_playlist_id"))

    def __repr__(self):
        return (
            f"\nPlaylist {self.kfjc_playlist_id}. {self.track_title} "
            f"from {self.album_title} by {self.artist} played on "
            f"{self.time_played}")


class Album(db.Model):
    """An album from the station."""

    __tablename__ = 'albums'

    kfjc_album_id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String(100))
    title = db.Column(db.String(100))
    is_collection = db.Column(db.Boolean)

    # tracks = a list of Track objects
    # playlist_tracks = a list of PlaylistTrack objects

    def __repr__(self):
        return f"\nAlbum {self.kfjc_album_id}: {self.artist}\t\t{self.title}"


class Track(db.Model):
    """A track from the station."""

    __tablename__ = 'tracks'

    id_ = db.Column(db.Integer, autoincrement=True, primary_key=True)
    kfjc_album_id = db.Column(
        db.Integer, ForeignKey("albums.kfjc_album_id"), nullable=True)
    artist = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(100))
    indx = db.Column(db.Integer)
    track = db.relationship(
        "Album", backref="tracks", cascade="all, delete-orphan",
        single_parent=True,
        primaryjoin="Track.kfjc_album_id == Album.kfjc_album_id")

    def __repr__(self):
        return (
            f"\n{self.id_}: Artist: {self.artist}, "
            f"Album {self.kfjc_album_id}, Track {self.indx}: {self.title}")


def connect_to_db(flask_app, db_uri=f"postgresql:///{DATABASE}", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print(f"Connected to {db_uri}")


if __name__ == "__main__":
    from server import app

    connect_to_db(app)
