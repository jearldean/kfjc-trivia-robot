import unittest

from server import app
from model import db, connect_to_db
import common
import users
import questions
import user_answers
import playlists
import playlist_tracks
import albums
import tracks
import collection_tracks

TEST_DATA_PATH = 'test_data/test_data.json'
DB_NAME = 'testdb'

class RobotTests(unittest.TestCase):
    """Tests for the KFJC Trivia Robot."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        # Connect to test database
        connect_to_db(app, f"postgresql:///{DB_NAME}")

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn(b"trivia question", result.data)


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
        self.make_users()
        self.make_questions()
        # possible_answers is just a testing device.
        self.possible_answers = questions.compile_possible_answers()
        self.make_user_answers()
        self.make_playlists()
        self.make_playlist_tracks()
        self.make_albums()
        self.make_tracks()
        self.make_collection_tracks()


    def make_users(self):
        """Add users from self.test_data."""
        for one_user in self.test_data["users"]:
            a, b, c, d = one_user  # unpack
            users.create_user(email=a, fname=b, password=c, salt=d)

    def make_questions(self):
        """Add questions from self.test_data."""
        for one_question in self.test_data["questions"]:
            a, b = one_question  # unpack
            questions.create_question(question=a, acceptable_answers=b)

    def make_user_answers(self):
        """Make 3 answers for each user: One PASS, FAIL, SKIP"""    
        user_instance = users.get_user_by_id(user_id=3)
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
            answer_given='')

    def make_playlists(self):
        """Add playlists from self.test_data."""
        for one_playlist in self.test_data["playlists"]:
            _, a, b, c, d, e = one_playlist  # unpack
            playlists.create_playlist(
                playlist_id=a, user_id=b, air_name=c, start_time=d, end_time=e)

    def make_playlist_tracks(self):
        """Add playlist_tracks from self.test_data."""
        for one_playlist_track in self.test_data["playlist_tracks"]:
            _, a, b, c, d, e, f, g, h, i = one_playlist_track  # unpack
            playlist_tracks.create_playlist_track(playlist_id=a, indx=b, 
                is_current=c, artist=d, track_title=e, album_title=f, 
                album_id=g, album_label=h, time_played=i)

    def make_albums(self):
        """Add playlists from self.test_data."""
        for one_album in self.test_data["albums"]:
            _, a, b, c, d = one_album  # unpack
            albums.create_album(album_id=a, artist=b, title=c, is_collection=d)

    def make_tracks(self):
        """Add tracks from self.test_data."""
        for one_track in self.test_data["tracks"]:
            _, a, b, c, d = one_track  # unpack
            tracks.create_track(album_id=a, title=b, indx=c, clean=d)

    def make_collection_tracks(self):
        """Add collection_tracks from self.test_data."""
        for one_collection_track in self.test_data["collection_tracks"]:
            _, a, b, c, d, e = one_collection_track  # unpack
            collection_tracks.create_collection_track(
                album_id=a, title=b, artist=c, indx=d, clean=e)

    def test_kfjc_trivia_robot_parts(self):
        """
        Learned the hard way: See https://stackoverflow.com/questions/
        45021216/when-unittesting-with-flask-flask-sqlalchemy-and-sqlalchemy-how-do-i-isolate
        Because it was really innefficient for me to separate each test out:
            set_up and tear_down run for EACH test_ function you have!
        """

        # Percy's user_id is 5:
        self.assertEquals("Percy", users.get_user_by_id(user_id=5).fname)

        # Charlie's email is charlie@dragon_preserve.ro:
        self.assertEquals(
            "Charlie", 
            users.get_user_by_email(email='charlie@dragon_preserve.ro').fname)

        # Arthur's email is arthur@ministry_of_magic.gov:
        self.assertEquals(
            "Arthur", 
            users.get_user_by_email(email='arthur@ministry_of_magic.gov').fname)

        # Arthur's email exists already:
        self.assertTrue(
            users.does_this_user_exist_already(email='arthur@ministry_of_magic.gov'))

        # This email is not in the db:
        self.assertFalse(
            users.does_this_user_exist_already(email='severus@death_eaters.org'))

        # Question 2 is 'Name a teacher.':
        self.assertEquals(
            "Name a teacher.",
            questions.get_question_by_id(question_id=2).question)

        # 'snape' is an acceptable_answer to Question 2:
        self.assertIn("snape", questions.get_question_by_id(question_id=2).acceptable_answers)

        # Any arbitrary answer for Question 2 should be in ['snape', 'mcgonigal']:
        self.assertIn(questions.get_one_right_answer(
            questions.get_question_by_id(question_id=2)), ['snape', 'mcgonigal'])

        # 'snitch' and 'draco' are in the compiled list of possible_answers:
        self.assertIn('snitch', self.possible_answers)
        self.assertIn('draco', self.possible_answers)
        # but 'horcrux' is not:
        self.assertNotIn('horcrux', self.possible_answers)

        # There should not be any correct answers in three_wrong_answers:
        three_wrong_answers = questions.get_three_wrong_answers(
            question_instance=questions.get_question_by_id(question_id=2), 
            possible_answers=self.possible_answers)
        for wrong_answer in three_wrong_answers:
            self.assertNotIn(wrong_answer, ['snape', 'mcgonigal'])

        # In make_user_answers() above, we assigned user_id 3
        # one correct answer, one wrong answer and one skipped question.
        # That should result in a user_score like this:
        #     {'passed': 1, 'failed': 1, 'skipped': 1, 'questions': 3, 'percent': 50.0}
        user_score = user_answers.get_user_score(users.get_user_by_id(user_id=3))
        self.assertEquals(1, user_score['passed'])
        self.assertEquals(1, user_score['failed'])
        self.assertEquals(1, user_score['skipped'])
        self.assertEquals(3, user_score['questions'])
        self.assertEquals(50, user_score['percent'])

        # playlist_id 66378 was a show by Sir Cumference.
        self.assertEquals(
            "Sir Cumference", 
            playlists.get_playlist_by_playlist_id(playlist_id=66378).air_name)

        # The first track on playlist_id 66377 was a Johnny Cash song.
        self.assertEquals(
            "Johnny Cash", 
            playlist_tracks.get_playlist_track_by_playlist_id_and_indx(
                playlist_id=66377, indx=1).artist)

        # The third track on playlist_id 66378 was titled 'The Hamilton Polka'.
        self.assertEquals(
            "The Hamilton Polka", 
            playlist_tracks.get_playlist_track_by_playlist_id_and_indx(
                playlist_id=66378, indx=3).track_title)

        # The first track on playlist_id 66378 was from the album 
        # "The Hitchhiker's Guide to the Galaxy"'.
        self.assertEquals(
            "The Hitchhiker's Guide to the Galaxy", 
            playlist_tracks.get_playlist_track_by_playlist_id_and_indx(
                playlist_id=66378, indx=1).album_title)

        # The Johnny Cash album was titled "Essential Johnny Cash - Disc 2".
        self.assertIn(
            "Essential Johnny Cash - Disc 2",
            albums.get_albums_by_artist(artist="Johnny Cash")[0].title)

        # The artist for album "Live At Reggae Sunsplash" is listed 
        # as "Various Artists Compilation".
        self.assertIn(
            "Various Artists Compilation",
            albums.get_albums_by_title(title="Live At Reggae Sunsplash")[0].artist)

        # There are 10 tracks on the one album in test_data.
        self.assertEquals(10, len(tracks.get_tracks()))

        # track_id = 1 (and not 303385) because we're throwing away the id_
        # in the sample data and reassigning it when we create new test tables:
        self.assertEquals("One Piece at a Time", tracks.get_track_by_id(track_id=1).title)

        # The word "Baby" should be found in a search for tracks containing the word "Baby".
        self.assertIn("Baby", collection_tracks.get_collection_tracks_with_word_in_title(
            word='Baby')[0].title)
        # There are 2 tracks that contain the word "Baby" in test_data.
        self.assertEquals(2,
            len(collection_tracks.get_collection_tracks_with_word_in_title(word='Baby')))


    def tearDown(self):
        """Stuff that runs after every def test_ function."""

        db.session.close()
        # Test Data is purged at the end of each test:
        db.drop_all()

if __name__ == "__main__":
    unittest.main()
