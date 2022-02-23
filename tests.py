import unittest

from server import app
from model import db, connect_to_db
import import_station_data
import playlists
import playlist_tracks
import albums
import tracks
import users
import questions
import answers
import common

TEST_DATA_PATH = 'test_data/test_data.json'
DB_NAME = 'testdb'

class RobotTests(unittest.TestCase):
    """Tests for the KFJC Trivia Robot."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        # Connect to test database
        connect_to_db(app, f"postgresql:///{DB_NAME}")

    """
    TODO Test ALL Routes:  '/'
    TODO Test ALL Routes:  '/login'
    TODO Test ALL Routes:  '/create_account'
    TODO Test ALL Routes:  '/important'
    TODO Test ALL Routes:  '/logout'
    TODO Test ALL Routes:  '/infopage'
    TODO Test ALL Routes:  '/score'
    TODO Test ALL Routes:  '/question'
    TODO Test ALL Routes:  '/ask'
    TODO Test ALL Routes:  '/answer'
    TODO Test ALL Routes:  '/ajax'
    TODO Test ALL Routes:  '/leaderboard'
    TODO Test ALL Routes:  REST API   '/playlists'
    TODO Test ALL Routes:  REST API   '/playlists/<int:id_>'
    TODO Test ALL Routes:  REST API   '/dj_favorites/<int:dj_id>'
    TODO Test ALL Routes:  REST API   '/last_played/artist=<string:artist>'
    TODO Test ALL Routes:  REST API   '/last_played/album=<string:album>'
    TODO Test ALL Routes:  REST API   '/last_played/track=<string:track>'
    TODO Test ALL Routes:  REST API   '/top_artists/top=<int:top>&start_date=<string:start_date>&end_date=<string:end_date>'
    TODO Test ALL Routes:  REST API   '/dj_stats/order_by=<string:order_by>&reverse=<int:reverse>'
    TODO Test ALL Routes:  REST API   '/dj_stats'
    TODO Test ALL Routes:  REST API   '/album_tracks/<int:kfjc_album_id>'

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn(b"trivia question", result.data)

    def test_question_page(self):
        result = self.client.get("/question")
        self.assertIn(b"?", result.data)

    def test_ask_page(self):
        result = self.client.get("/ask")
        self.assertIn(b"You can ask about DJs", result.data)
        
    """


class RobotTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""
    test_data = common.open_json_files(TEST_DATA_PATH)
    possible_answers = []

    def setUp(self):
        """Stuff that runs before every def test_ function."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        connect_to_db(flask_app=app, db_uri=f"postgresql:///{DB_NAME}")
        db.drop_all()
        db.create_all()

        # Fill the testdb:
        #self.make_users()
        # possible_answers is just a testing device.
        # self.possible_answers = questions.compile_possible_answers()
        # self.make_user_answers()
        import_station_data.add_missing_albums()
        self.make_albums()  # Just like in import_station_data, albums must seed first.
        self.make_playlists()
        self.make_playlist_tracks()
        self.make_tracks()
        self.make_collection_tracks()

        #self.make_questions()

    def make_users(self):
        """Add users from self.test_data."""
        for one_user in self.test_data["users"]:
            a, b, c, d = one_user  # unpack
            users.create_user(email=a, fname=b, password=c, salt=d)

    def make_questions(self):
        """Add questions."""
        questions.SEED_QUESTION_COUNT = 1
        questions.make_all_the_questions()

    def make_user_answers(self):
        """Make 3 answers for each user: One PASS, FAIL, SKIP   
        user_instance = users.get_user_by_id(user_id=3)
        answers.create_answer(user_instance=user_instance, question_instance, answer_given)


        user_answers.create_user_answer(
            user_instance=user_instance,
            question_instance=questions.get_question_by_id(question_id=9), 
            answer_given='snitch')
        user_answers.create_user_answer(
            user_instance=user_instance,
            question_instance=questions.get_question_by_id(question_id=8), 
            answer_given='snitch')
        user_answers.create_user_answer(
            user_instance=user_instance,
            question_instance=questions.get_question_by_id(question_id=7), 
            answer_given='')""" 
        pass

    def import_station_data(data_path_and_function):
        for each_tuple in data_path_and_function:
            file_path, row_handler = each_tuple  # unpack
            import_station_data.seed_a_large_csv(file_path=file_path, row_handler=row_handler)

    def make_playlists(self):
        """Add playlists from test_data/station_data/playlist.csv."""
        import_station_data.seed_a_large_csv(
            file_path='test_data/station_data/playlist.csv',
            row_handler=import_station_data.create_playlists)

    def make_playlist_tracks(self):
        """Add playlist_tracks from test_data/station_data/playlist_track.csv."""
        import_station_data.seed_a_large_csv(
            file_path='test_data/station_data/playlist_track.csv',
            row_handler=import_station_data.create_playlist_tracks)

    def make_albums(self):
        """Add albums from test_data/station_data/album.csv."""
        import_station_data.seed_a_large_csv(
            file_path='test_data/station_data/album.csv',
            row_handler=import_station_data.create_albums)

    def make_tracks(self):
        """Add tracks from test_data/station_data/track.csv."""
        import_station_data.seed_a_large_csv(
            file_path='test_data/station_data/track.csv',
            row_handler=import_station_data.create_tracks)

    def make_collection_tracks(self):
        """Add collection_tracks from test_data/station_data/coll_track.csv."""
        import_station_data.seed_a_large_csv(
            file_path='test_data/station_data/coll_track.csv',
            row_handler=import_station_data.create_collection_tracks)

    def test_kfjc_trivia_robot_parts(self):
        """
        Learned the hard way: See https://stackoverflow.com/questions/
        45021216/when-unittesting-with-flask-flask-sqlalchemy-and-sqlalchemy-how-do-i-isolate
        Because it was really innefficient for me to separate each test out:
            set_up and tear_down run for EACH test_ function you have!

            https://medium.com/@dirk.avery/pytest-modulenotfounderror-no-module-named-requests-a770e6926ac5
        """
        
        # TODO   answers.get_user_score(user_instance)
        # TODO   answers.is_answer_correct(question_instance, answer_given)
        # TODO   common.get_count(table_dot_column, unique=True)
        # TODO   get_ages(table_dot_column)
        # TODO   import_station_data. no bad times  ["0000-00-00 00:00:00", "1970-01-01 01:00:00", "1969-12-31 16:00:00"]
        # TODO   import_station_data. profanity filter
        # TODO   import_station_data. time estimator
        # TODO   import_station_data. other data smoothing.
        # TODO   playlist_tracks.get_favorite_artists(dj_id, reverse=True, min_plays=5):
        # TODO   playlist_tracks.get_favorite_albums(dj_id, reverse=True, min_plays=5):
        # TODO   playlist_tracks.get_favorite_tracks(dj_id, reverse=True, min_plays=5)
        # TODO   playlist_tracks.get_top10_artists(start_date, end_date, n=10)
        # TODO   playlist_tracks.get_top10_albums(start_date, end_date, n=10)
        # TODO   playlist_tracks.get_top10_tracks(start_date, end_date, n=10)
        # TODO   playlist_tracks.get_a_random_artist(min_appearances=3)
        # TODO   playlist_tracks.get_a_random_album(min_appearances=3)
        # TODO   playlist_tracks.get_a_random_track(min_appearances=3)
        # TODO   playlist_tracks.get_last_play_of_artist(artist, reverse=False)
        # TODO   playlist_tracks.get_last_play_of_album(album, reverse=False)
        # TODO   playlist_tracks.get_last_play_of_track(track, reverse=False)
        
        self.assertEqual(88, playlist_tracks.how_many_tracks())
        # TODO   playlists.get_djs_by_dj_id(reverse=False)
        # TODO   playlists.get_djs_alphabetically(reverse=False)
        # TODO   playlists.get_djs_by_first_show(reverse=False)
        # TODO   playlists.get_djs_by_last_show(reverse=False)
        # TODO   playlists.get_djs_by_show_count(reverse=False)

        # TODO   playlists.first_show_last_show()
        # TODO   playlists.get_all_dj_ids()
        # TODO   playlists.how_many_djs()
        # TODO   BROKEN. self.assertEqual(8, playlists.how_many_djs())

        self.assertEqual("Sir Cumference", playlists.get_airname(dj_id=255))
        self.assertEqual("DJ Click", playlists.get_airname(dj_id=324))
        self.assertEqual("Dr Doug", playlists.get_airname(dj_id=391))

        self.assertEqual(13, playlists.how_many_shows())

        # TODO   questions.make_all_the_questions()  # Seed 1 each... 14 Q's
        # TODO   questions.get_unique_question(user_id)  # Can't be answered already.

        for track in tracks.get_tracks_by_kfjc_album_id(kfjc_album_id=397830):
            self.assertEqual('Dolly Parton', track[1])

        self.assertEqual('Jolene', tracks.get_tracks_by_kfjc_album_id(kfjc_album_id=397830)[0][2])

        # TODO   users.get_users()
        # TODO   users.get_user_by_id(user_id)
        # TODO   users.get_user_by_username(username)
        # TODO   users.does_user_exist_already(username)
        # TODO   users.does_password_match(plain_text_password, hashed_password)

    def tearDown(self):
        """Stuff that runs after every def test_ function."""

        db.session.close()
        # Test Data is purged at the end of each test:
        db.drop_all()

if __name__ == "__main__":
    unittest.main()