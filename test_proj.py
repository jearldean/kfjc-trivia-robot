"""Tests for the KFJC Trivia Robot"""

import unittest
import datetime

from server import app
from model import db, connect_to_db
import import_station_data
import djs
import playlists
import playlist_tracks
import albums
import tracks
import users
import questions
import answers
import common

TEST_USERS_DATA_PATH = 'test_data/fake_users.json'
TEST_DJ_DATA_PATH = 'test_data/station_data/user.csv'
TEST_PLAYLIST_DATA_PATH = 'test_data/station_data/playlist.csv'
TEST_PLAYLIST_TRACK_DATA_PATH = 'test_data/station_data/playlist_track.csv'
TEST_ALBUM_DATA_PATH = 'test_data/station_data/album.csv'
TEST_TRACK_DATA_PATH = 'test_data/station_data/track.csv'
TEST_COLLECTION_TRACK_DATA_PATH = 'test_data/station_data/coll_track.csv'
TEST_DB_NAME = 'test_trivia'


class RobotTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""
    test_data = common.open_json_files(TEST_USERS_DATA_PATH)

    rest_api_parameterized_tests = [
        ["/playlists/60340", b"Sir Cumference"],
        ["/playlist_tracks/60706", b"James Brown"],
        ["/dj_favorites/artist/dj_id=177", b"Delixx"],
        ["/dj_favorites/album/dj_id=177", b"Uprising in Dub"],
        ["/dj_favorites/track/dj_id=177", b"Zion Train Dub"],
        ["/last_played/artist=JAMES%20BROWN", b"2019-11-26T02:01:15"],
        ["/last_played/album=Matching%20tie", b"2019-10-06T11:57:36"],
        ["/last_played/track=Spanish%20Inquisition", b"2019-10-06T11:57:36"],
        # Didn't expect that.
        [("/top_plays/top=5&order_by=artist&start_date=2000-01-02&"
          "end_date=2020-01-10"), b"The Meditations"],
        ["/top_plays/top=5&order_by=artists&start_date=2001-01-02&"
         "end_date=2021-01-10", b"The Meditations"],
        ["/top_plays/top=5&order_by=album&start_date=2002-01-02&"
         "end_date=2022-01-10", b"The Meditations"],
        ["/top_plays/top=5&order_by=albums&start_date=2000-01-02&"
         "end_date=2020-01-10", b"The Meditations"],
        ["/top_plays/top=5&order_by=track&start_date=2000-01-02&"
         "end_date=2020-01-10", b"The Meditations"],
        ["/dj_stats", b"Cy Thoth"],
        ["/dj_stats/order_by=air_name&reverse=1", b"DJ Click"],
        ["/dj_stats/order_by=air_name&reverse=0", b"Sir Cumference"],
        ["/dj_stats/order_by=dj_id&reverse=1", b"Spliff Skankin"],
        ["/dj_stats/order_by=showcount&reverse=1", b"Spliff Skankin"],
        ["/dj_stats/order_by=firstshow&reverse=0", b"Sir Cumference"],
        ["/dj_stats/order_by=lastshow&reverse=1", b"Cy Thoth"],
        ["/album_tracks/184227", b"Reality Dub"],
        ["/album_tracks/556860", b"Calendar"],
        ["/album_tracks/331805", b"Hoochie Coochie Man"],
        ["/artists_albums/artist=meditations", b"Greatest Hits"],
        ["/artists_albums/artist=Jonestown%20Massacre", b"Zero"],
        ["/artists_albums/artist=Harry", b"Love"]]

    def setUp(self):
        """Stuff that runs before every def test_ function."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        connect_to_db(flask_app=app, db_uri=f"postgresql:///{TEST_DB_NAME}")
        db.drop_all()
        db.create_all()

    def make_users(self):
        """Add users from self.test_data."""
        for one_user in self.test_data["users"]:
            username, fname, password = one_user  # unpack
            users.create_a_user(
                username=username, fname=fname, password=password)
        db.session.commit()

    def make_answers(self):
        """Make 3 answers for each user: One PASS, FAIL, SKIP."""
        question = questions.get_question_by_id(question_id=1)
        cheat_peek_at_answer = question.acceptable_answer
        for each_user in users.get_users():
            answers.create_answer(
                user_instance=each_user,
                question_instance=question,
                answer_given='SKIP')
            answers.create_answer(
                user_instance=each_user,
                question_instance=question,
                answer_given='wrong answer')
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
        import_station_data.DJ_DATA_PATH = (
            TEST_DJ_DATA_PATH)
        import_station_data.PLAYLIST_DATA_PATH = (
            TEST_PLAYLIST_DATA_PATH)
        import_station_data.PLAYLIST_TRACK_DATA_PATH = (
            TEST_PLAYLIST_TRACK_DATA_PATH)
        import_station_data.ALBUM_DATA_PATH = (
            TEST_ALBUM_DATA_PATH)
        import_station_data.TRACK_DATA_PATH = (
            TEST_TRACK_DATA_PATH)
        import_station_data.COLLECTION_TRACK_DATA_PATH = (
            TEST_COLLECTION_TRACK_DATA_PATH)

        # Import Station Data:
        import_station_data.import_all_tables()

        self.assertTrue(
            albums.get_album_by_id(kfjc_album_id=694447).is_collection)
        self.assertFalse(
            albums.get_album_by_id(kfjc_album_id=695055).is_collection)

        # Testing the Profanity Filter:
        self.assertNotIn(
            "Fuck", albums.get_album_by_id(kfjc_album_id=140533).title)
        self.assertNotIn(
            "Pussy", albums.get_album_by_id(kfjc_album_id=140533).title)

        self.assertEqual(
            "The Meditations",
            playlist_tracks.get_favorite_artists(
                dj_id=177, reverse=True, min_plays=5)[0].artist)
        self.assertEqual(
            "Monty Python\'s Previous Record",
            playlist_tracks.get_favorite_albums(
                dj_id=255, reverse=True, min_plays=5)[0].album_title)
        self.assertEqual(
            "Zion Train Dub",
            playlist_tracks.get_favorite_tracks(
                dj_id=177, reverse=True, min_plays=5)[0].track_title)

        self.assertEqual(
            "Delixx",
            playlist_tracks.get_top10_artists(
                start_date='2002-01-02', end_date='2022-01-10',
                n=5)[0].artist)
        self.assertEqual(
            "Uprising in Dub",
            playlist_tracks.get_top10_albums(
                start_date='2002-01-02', end_date='2022-01-10',
                n=5)[0].album_title)
        self.assertEqual(
            "Zion Train Dub",
            playlist_tracks.get_top10_tracks(
                start_date='2002-01-02', end_date='2022-01-10',
                n=5)[0].track_title)
        self.assertEqual(
            "Zion Train Dub",
            playlist_tracks.get_top10_tracks(
                start_date='2022-01-10', end_date='2002-01-02',
                n=5)[0].track_title)

        self.assertEqual(
            'The Meditations',
            playlist_tracks.get_favorite_artists(
                dj_id=177, min_plays=5)[0].artist)
        self.assertEqual(9, playlist_tracks.get_favorite_artists(
            dj_id=177, min_plays=5)[0].plays)

        self.assertIn(
            playlist_tracks.get_a_random_artist(min_appearances=6),
            ['The Meditations', "Delixx"])
        self.assertIn(
            playlist_tracks.get_a_random_album(min_appearances=3),
            ['Greatest Hits', 'Message From the Meditations',
             'Another Monty Python Record',
             "Monty Python's Previous Record", 'Matching Tie & Handkerchief',
             "Monty Python's Contractual Obligation Album", 'Uprising in Dub'])
        self.assertIn(
            playlist_tracks.get_a_random_track(min_appearances=5),
            ["Zion Train Dub"])

        self.assertEqual(
            "Dr Doug",
            playlist_tracks.get_last_play_of_artist(
                artist="Brother Ali")[0].air_name)
        self.assertEqual(
            "Dr Doug",
            playlist_tracks.get_last_play_of_album(
                album="Shadows on the Sun")[0].air_name)
        self.assertEqual(
            "Dr Doug",
            playlist_tracks.get_last_play_of_track(
                track="Star Quality")[0].air_name)
        self.assertEqual(
            "BLM - Rock and Hip Hop",
            playlist_tracks.get_last_play_of_artist(
                artist="hip  hop")[0].artist)
        self.assertEqual(
            "BLM - Rock and Hip Hop",
            playlist_tracks.get_last_play_of_artist(
                artist=" h i p  h o p ")[0].artist)

        # Also tests: common.get_count(table_dot_column, unique=True)
        self.assertEqual(97, playlist_tracks.how_many_tracks())

        playlists.MIN_SHOW_COUNT = 0
        self.assertEqual('Cy Thoth', playlists.get_djs_by_dj_id()[0].air_name)
        self.assertEqual(
            "dr doug", playlists.get_djs_by_dj_id(reverse=True)[0].air_name)

        self.assertEqual(
            'Cy Thoth', playlists.get_djs_alphabetically()[0].air_name)
        self.assertEqual(
            "Spliff Skankin",
            playlists.get_djs_alphabetically(reverse=True)[0].air_name)

        self.assertEqual(
            "Spliff Skankin", playlists.get_djs_by_first_show()[0].air_name)
        self.assertEqual('dr doug', playlists.get_djs_by_first_show(
            reverse=True)[0].air_name)

        self.assertIn(
            playlists.get_djs_by_last_show()[0].air_name,
            ["Robert Emmett", 'dr doug'])
        self.assertEqual(
            "dr doug",
            playlists.get_djs_by_last_show(reverse=True)[0].air_name)

        self.assertIn(
            playlists.get_djs_by_show_count()[0].air_name,
            ["Robert Emmett", 'dr doug'])
        self.assertEqual(
            "Spliff Skankin",
            playlists.get_djs_by_show_count(reverse=True)[0].air_name)

        self.assertEqual((
            datetime.datetime(2000, 8, 13, 16, 0),
            datetime.datetime(2022, 2, 16, 2, 0, 30)),
            playlists.first_show_last_show())
        # Another way to do it:
        oldest, newest = playlists.first_show_last_show()
        self.assertEqual(oldest.isoformat(), "2000-08-13T16:00:00")
        self.assertEqual(newest.isoformat(), "2022-02-16T02:00:30")

        self.assertEqual(
            1, playlists.get_dj_ids_and_show_counts()[0].showcount)
        self.assertEqual(431, playlists.get_dj_ids_and_show_counts()[0].dj_id)
        self.assertEqual(7, playlists.how_many_djs())

        self.assertEqual("Sir Cumference", djs.get_airname_for_dj(
            dj_id=255, posessive=False))
        self.assertEqual("Sir Cumference's", djs.get_airname_for_dj(
            dj_id=255, posessive=True))
        self.assertEqual("♡ Cy Thoth ♡", djs.get_airname_for_dj(
            dj_id=41, posessive=False))
        self.assertEqual("♡ Cy Thoth's ♡", djs.get_airname_for_dj(
            dj_id=41, posessive=True))

        self.assertEqual(18, playlists.how_many_shows())

        for track in tracks.get_tracks_by_kfjc_album_id(kfjc_album_id=397830):
            self.assertEqual('Dolly Parton', track.artist)
        self.assertEqual(
            'Jolene', tracks.get_tracks_by_kfjc_album_id(
                kfjc_album_id=397830)[0].title)

        self.make_users()
        self.assertEqual("Percy", users.get_user_by_id(user_id=5).fname)
        self.assertEqual(
             "Charlie",
             users.get_user_by_username(
                 username='charlie@dragon_preserve.ro').fname)
        self.assertEqual(
             "Arthur",
             users.get_user_by_username(
                 username='arthur@ministry_of_magic.gov').fname)
        self.assertTrue(users.does_user_exist_already(
            username='arthur@ministry_of_magic.gov'))
        self.assertFalse(users.does_user_exist_already(
            username='severus@death_eaters.org'))
        self.assertTrue(users.does_password_match(
            user_instance=users.get_user_by_id(user_id=5),
            password_from_form="prefect"))
        self.assertFalse(users.does_password_match(
            user_instance=users.get_user_by_id(user_id=5),
            password_from_form="perCyIzAw3sum"))

        questions.SEED_QUESTION_COUNT = 1
        questions.make_all_questions()

        self.make_answers()
        # Also tests: answers.is_answer_correct(
        #   question_instance, answer_given)
        percys_score = answers.get_user_score(user_id=5)
        self.assertEqual(1, percys_score.passed)
        self.assertEqual(1, percys_score.failed)
        self.assertEqual(1, percys_score.skipped)
        self.assertEqual(3, percys_score.questions)
        self.assertEqual(50, percys_score.percent)
        self.assertNotEqual(1, questions.get_unique_question(user_id=5))

        result = self.client.post(
            "/login",
            data={
                "username": "fred@weasleyswizardingwheezes.com",
                "password": "georgeDidIt"},
            follow_redirects=True)
        self.assertIn(b"A Question about", result.data)
        self.assertNotIn(b"%", result.data)

        for each_test in self.rest_api_parameterized_tests:
            result = self.client.get(each_test[0])
            print("jem", each_test, result.data)
            self.assertIn(each_test[1], result.data)

    def tearDown(self):
        """Stuff that runs after every def test_ function."""

        db.session.close()
        # Test Data is purged at the end of each test:
        db.drop_all()


if __name__ == "__main__":
    unittest.main()  # pytest --tb=long
