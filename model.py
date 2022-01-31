"""Models for KFJC Trivia Robot."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DATABASE = "trivia"  # Make sure this agrees with your seed.py program...


class User(db.Model):
    """A user."""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    fname = db.Column(db.String(30), unique=False, nullable=True)
    password = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable=False)
    # user_answers = a list of UserAnswer objects

    def __repr__(self):
        spaces = (13 - len(self.fname)) * " "
        return (f"\nU:{self.user_id}\t{self.fname}{spaces}{self.email}")


class Question(db.Model):
    """A question."""

    __tablename__ = 'questions'

    question_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    question = db.Column(db.String, nullable=False)
    acceptable_answers = db.Column(db.PickleType, nullable=False)
    # user_answers = a list of UserAnswers objects

    def __repr__(self):
        spaces = (25 - len(self.question)) * " "
        return (f"\nQ:{self.question_id}\t{self.question}{spaces}{self.acceptable_answers}")


class UserAnswer(db.Model):
    """A response from a user."""

    __tablename__ = 'user_answers'

    user_answer_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    question_id = db.Column(db.Integer, db.ForeignKey("questions.question_id"))
    answer_given = db.Column(db.String, nullable=True)
    answer_correct = db.Column(db.Boolean, nullable=True)
    timestamp = db.Column(db.DateTime)

    question = db.relationship("Question", backref="user_answers")
    user = db.relationship("User", backref="user_answers")

    def __repr__(self):
        return f"\nA:{self.user_answer_id}\tU:{self.user_id}\tQ:{self.question_id}\t{self.answer_given}\t{self.answer_correct}\t{self.timestamp}"


class Playlist(db.Model):
    """A playlist from the station."""

    __tablename__ = 'playlists'

    id_ = db.Column(db.Integer, autoincrement=True, primary_key=True)
    playlist_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    air_name = db.Column(db.String(60), nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)  # '2022-01-19 22:04:31'
    end_time = db.Column(db.DateTime, nullable=True)  # '2022-01-19 22:08:42'

    
    def __repr__(self):
        #return f"\n{self.playlist_id}. {self.air_name} on {self.start_time}"
        return f"{self.id_}, {self.playlist_id}, {self.user_id}, {self.air_name}, {self.start_time}, {self.end_time}"


class PlaylistTrack(db.Model):
    """A playlist track from the station."""

    __tablename__ = 'playlist_tracks'

    id_ = db.Column(db.Integer, autoincrement=True, primary_key=True)
    playlist_id = db.Column(db.Integer)
    indx = db.Column(db.Integer, nullable=True)
    is_current = db.Column(db.SmallInteger, nullable=True)
    artist = db.Column(db.String(100))
    track_title = db.Column(db.String(100))
    album_title = db.Column(db.String(100))
    album_id = db.Column(db.Integer, nullable=True)
    album_label = db.Column(db.String(100), nullable=True)
    time_played = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        #return f"\nPlaylist {self.playlist_id}. {self.track_title} from {self.album_title} by {self.artist} played on {self.time_played}"
        return f"{self.playlist_id}, {self.is_current}, {self.artist}, {self.track_title}, {self.album_title}, {self.album_id}, {self.album_label}, {self.time_played}"


class Album(db.Model):
    """An album from the station."""

    __tablename__ = 'albums'

    id_ = db.Column(db.Integer, autoincrement=True, primary_key=True)
    album_id = db.Column(db.Integer)
    artist = db.Column(db.String(100))
    title = db.Column(db.String(100))
    is_collection = db.Column(db.SmallInteger)

    def __repr__(self):
        return f"\nAlbum {self.album_id}: {self.artist}\t\t{self.title}"


class Track(db.Model):
    """A track from the station."""

    __tablename__ = 'tracks'

    id_ = db.Column(db.Integer, autoincrement=True, primary_key=True)
    album_id = db.Column(db.Integer)
    title = db.Column(db.String(100))
    indx = db.Column(db.Integer)
    clean = db.Column(db.SmallInteger)

    def __repr__(self):
        return f"\nid_{self.id_}\tAlbum {self.album_id}, Track {self.indx}: {self.title}"


class CollectionTrack(db.Model):
    """A collection_track from the station."""

    __tablename__ = 'collection_tracks'

    id_ = db.Column(db.Integer, autoincrement=True, primary_key=True)
    album_id = db.Column(db.Integer)
    title = db.Column(db.String(100), nullable=True)
    artist = db.Column(db.String(100), nullable=True)
    indx = db.Column(db.Integer)
    clean = db.Column(db.SmallInteger)

    def __repr__(self):
        return f"\nAlbum {self.album_id}, Track {self.indx}: {self.title} by {self.artist}"


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
