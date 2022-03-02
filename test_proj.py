"""Tests for the KFJC Trivia Robot"""

import unittest
import datetime

from server import app
from model import Playlist, db, connect_to_db
import import_station_data
import playlists
import playlist_tracks
import albums
import tracks
import users
import questions
import answers
import common

TEST_DATA_PATH = 'test_data/fake_users.json'
DB_NAME = 'testdb'

class RobotTests(unittest.TestCase):
    """Tests for the KFJC Trivia Robot."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        # Connect to test database
        connect_to_db(app, f"postgresql:///{DB_NAME}")

        """
        db.drop_all()
        db.create_all()

        # Overwrite default paths:
        import_station_data.PLAYLIST_DATA_PATH = 'test_data/station_data/playlist.csv'
        import_station_data.PLAYLIST_TRACK_DATA_PATH = 'test_data/station_data/playlist_track.csv'
        import_station_data.ALBUM_DATA_PATH = 'test_data/station_data/album.csv'
        import_station_data.TRACK_DATA_PATH = 'test_data/station_data/track.csv'
        import_station_data.COLLECTION_TRACK_DATA_PATH = 'test_data/station_data/coll_track.csv'

        # Import Station Data:
        import_station_data.import_all_tables()

        rtd = RobotTestsDatabase()
        rtd.make_users()
        rtd.make_questions()
        rtd.make_answers()

        TODO Test ALL Routes:  '/'

        def test_homepage(self):
            result = self.client.get("/")
            self.assertIn(b"trivia question", result.data)


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
            
        #def test_rest_dj_stats(self):
        #    result = self.client.get("dj_stats/order_by=dj_id&reverse=1")
        #    self.assertIn(b"Spliff Skankin", result.data[0]['air_name'])
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

    def make_users(self):
        """Add users from self.test_data."""
        for one_user in self.test_data["users"]:
            username, fname, password = one_user  # unpack
            users.create_a_user(username=username, fname=fname, password=password)
        db.session.commit()

    def make_answers(self):
        """Make 3 answers for each user: One PASS, FAIL, SKIP."""
        question = questions.get_question_by_id(question_id=1)
        cheat_peek_at_answer = question.acceptable_answers[0]
        for each_user in users.get_users():
            answers.create_answer(
                user_instance=each_user,
                question_instance=question,
                answer_given='SKIP')
            answers.create_answer(
                user_instance=each_user,
                question_instance=question,
                answer_given='Sir Cumference')
            answers.create_answer(
                user_instance=each_user,
                question_instance=question,
                answer_given=cheat_peek_at_answer)
                
    def test_kfjc_trivia_robot_parts(self):
        """
        Learned the hard way: See https://stackoverflow.com/questions/
        45021216/when-unittesting-with-flask-flask-sqlalchemy-and-sqlalchemy-how-do-i-isolate
        Because it was really innefficient for me to separate each test out:
            set_up and tear_down run for EACH test_ function you have!

        https://medium.com/@dirk.avery/pytest-modulenotfounderror-no-module-named-requests-a770e6926ac5
        """

        # Overwrite default paths:
        import_station_data.PLAYLIST_DATA_PATH = 'test_data/station_data/playlist.csv'
        import_station_data.PLAYLIST_TRACK_DATA_PATH = 'test_data/station_data/playlist_track.csv'
        import_station_data.ALBUM_DATA_PATH = 'test_data/station_data/album.csv'
        import_station_data.TRACK_DATA_PATH = 'test_data/station_data/track.csv'
        import_station_data.COLLECTION_TRACK_DATA_PATH = 'test_data/station_data/coll_track.csv'

        # Import Station Data:
        import_station_data.import_all_tables()
        
        #695055,"Hiatt, John","Open Road, The","C","C","F",NULL,"0","L",NULL,"2010-04-07","2010-06-04",20088,1,0,"0000-00-00","0000-00-00"
        #694447,"[coll]: Sister Funk 2","Sister Funk 2","G","V","F",NULL,"1","L",NULL,"2010-03-24","2010-06-04",8871,NULL,0,"0000-00-00","0000-00-00"
        self.assertTrue(albums.get_album_by_id(kfjc_album_id=694447).is_collection)
        self.assertFalse(albums.get_album_by_id(kfjc_album_id=695055).is_collection)
        
        oldest, newest = common.get_ages(Playlist.start_time)
        self.assertEqual(oldest.isoformat(), "2000-08-13T16:00:00")
        self.assertEqual(newest.isoformat(), "2022-02-16T02:00:30")

        self.assertNotIn("Fuck", albums.get_album_by_id(kfjc_album_id=140533).title)
        self.assertNotIn("Pussy", albums.get_album_by_id(kfjc_album_id=140533).title)

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
        self.assertEqual('The Meditations', playlist_tracks.get_favorite_artists(dj_id=177, min_plays=5)[0].artist)
        self.assertEqual(9, playlist_tracks.get_favorite_artists(dj_id=177, min_plays=5)[0].plays)
        # self.assertEqual('The Meditations', playlist_tracks.get_a_random_artist(min_appearances=4))
        self.assertIn(playlist_tracks.get_a_random_album(min_appearances=3), [
            "Greatest Hits", "Message From the Meditations", 
            'Another Monty Python Record', "Monty Python's Previous Record", 
            'Matching Tie & Handkerchief', "Monty Python's Contractual Obligation Album"])
        # TODO self.assertIn(playlist_tracks.get_a_random_track(min_appearances=2), [])
        # TODO playlist_tracks.get_a_random_track(min_appearances=0)
        # self.assertEqual('Zion Train Dub', playlist_tracks.get_a_random_track(min_appearances=2))
        
        self.assertEqual('Dr Doug', playlist_tracks.get_last_play_of_artist(artist="Brother Ali")[0].air_name)
        self.assertEqual('Dr Doug', playlist_tracks.get_last_play_of_album(album="Shadows on the Sun")[0].air_name)
        self.assertEqual('Dr Doug', playlist_tracks.get_last_play_of_track(track="Star Quality")[0].air_name)

        # Also tests: common.get_count(table_dot_column, unique=True)
        self.assertEqual(124, playlist_tracks.how_many_tracks())

        playlists.MIN_SHOW_COUNT = 0
        self.assertEqual('Cy Thoth', playlists.get_djs_by_dj_id()[0].air_name)
        self.assertEqual("Dr Doug", playlists.get_djs_by_dj_id(reverse=True)[0].air_name)

        self.assertEqual('Cy Thoth', playlists.get_djs_alphabetically()[0].air_name)
        self.assertEqual("Spliff Skankin'", playlists.get_djs_alphabetically(reverse=True)[0].air_name)

        self.assertEqual("Spliff Skankin'", playlists.get_djs_by_first_show()[0].air_name)
        self.assertEqual('Dr Doug', playlists.get_djs_by_first_show(reverse=True)[0].air_name)

        self.assertIn(
            playlists.get_djs_by_last_show()[0].air_name,
            ["Robert Emmett", 'Dr Doug'])
        self.assertEqual("Dr Doug", playlists.get_djs_by_last_show(reverse=True)[0].air_name)

        self.assertIn(
            playlists.get_djs_by_show_count()[0].air_name,
            ["Robert Emmett", 'Dr Doug'])
        self.assertEqual("Spliff Skankin'", playlists.get_djs_by_show_count(reverse=True)[0].air_name)
        
        self.assertEqual(
            (datetime.datetime(2000, 8, 13, 16, 0), 
            datetime.datetime(2022, 2, 16, 2, 0, 30)), 
            playlists.first_show_last_show())
        
        self.assertEqual(1, playlists.get_dj_ids_and_show_counts()[0].showcount)
        self.assertEqual(431, playlists.get_dj_ids_and_show_counts()[0].dj_id)
        self.assertEqual(8, playlists.how_many_djs())

        self.assertEqual("Sir Cumference", playlists.get_airname(dj_id=255))
        self.assertEqual("DJ Click", playlists.get_airname(dj_id=324))
        self.assertEqual("Dr Doug", playlists.get_airname(dj_id=391))

        self.assertEqual(14, playlists.how_many_shows())

        for track in tracks.get_tracks_by_kfjc_album_id(kfjc_album_id=397830):
            self.assertEqual('Dolly Parton', track.artist)
        self.assertEqual(
            'Jolene', tracks.get_tracks_by_kfjc_album_id(kfjc_album_id=397830)[0].title)

        self.make_users()
        self.assertEqual("Percy", users.get_user_by_id(user_id=5).fname)
        self.assertEqual(
             "Charlie", 
             users.get_user_by_username(username='charlie@dragon_preserve.ro').fname)
        self.assertEqual(
             "Arthur", 
             users.get_user_by_username(username='arthur@ministry_of_magic.gov').fname)
        self.assertTrue(users.does_user_exist_already(username='arthur@ministry_of_magic.gov'))
        self.assertFalse(users.does_user_exist_already(username='severus@death_eaters.org'))
        self.assertTrue(users.does_password_match(
            user_instance = users.get_user_by_id(user_id=5), 
            password_from_form = "prefect"))
        self.assertFalse(users.does_password_match(
            user_instance = users.get_user_by_id(user_id=5), 
            password_from_form = "perCyIzAw3sum"))
        
        questions.SEED_QUESTION_COUNT = 1
        questions.make_all_questions()

        self.make_answers()
        # Also tests: answers.is_answer_correct(question_instance, answer_given)
        percys_score = answers.get_user_score(user_id=5)
        self.assertEqual(1, percys_score['passed'])
        self.assertEqual(1, percys_score['failed'])
        self.assertEqual(1, percys_score['skipped'])
        self.assertEqual(3, percys_score['questions'])
        self.assertEqual(50, percys_score['percent'])
        self.assertNotEqual(1, questions.get_unique_question(user_id=5))
        
    def tearDown(self):
        """Stuff that runs after every def test_ function."""

        db.session.close()
        # Test Data is purged at the end of each test:
        db.drop_all()

if __name__ == "__main__":
    unittest.main()  # pytest --tb=long
