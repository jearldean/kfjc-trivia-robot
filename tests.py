import unittest

from server import app
from model import db, connect_to_db, User, Question, UserAnswer
import crud


class RobotTests(unittest.TestCase):
    """Tests for the KFJC Trivia Robot."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn(b"trivia question", result.data)


class RobotTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    test_users = [
        ['arthur@ministry_of_magic.gov', 'Arthur', 'test', 'test'],
        ['molly@theburrough.com', 'Molly', 'test', 'test'],
        ['bill@ministry_of_magic.gov', 'Bill', 'test', 'test'],
        ['charlie@dragon_preserve.ro', 'Charlie', 'test', 'test'],
        ['percy@hogwarts.edu', 'Percy', 'test', 'test'],
        ['fred@weasleyswizardingwheezes.com', 'Fred', 'test', 'test'],
        ['george@weasleyswizardingwheezes.com', 'George', 'test', 'test'],
        ['ron@hogwarts.edu', 'Ron', 'test', 'test'],
        ['ginny@hogwarts.edu', 'Ginny', 'test', 'test']]

    test_questions = [
        ["Name a spell.", ['expelliarmus', 'alohamora']],
        ["Name a teacher.", ['snape', 'mcgonigal']],
        ["Name a headmaster.", ['dumbledore']],
        ["Name a gryffindor.", ['harry', 'ron', 'hermione']],
        ["Name a slytherin.", ['draco', 'severus', 'salizar']],
        ["Name a hufflepuff.", ['cedric']],
        ["Name a ravenclaw.", ['luna', 'cho']],
        ["Name a broom.", ['nimbus 2000', 'cleansweep 7', 'silver arrow']],
        ["Name a quidditch ball.", ['snitch', 'bludger', 'quaffle']]]
    
    test_answers = []

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        db_name = 'testdb'
        connect_to_db(flask_app=app, db_uri=f"postgresql:///{db_name}")
        db.drop_all()
        db.create_all()

    def make_users(self):
        """Add all entries in self.test_users"""
        for one_weasley in self.test_users:
            crud.create_user(
                email=one_weasley[0], fname=one_weasley[1],
                password=one_weasley[2], salt=one_weasley[3])

    def make_questions(self):
        """Add all entries in self.test_questions"""
        for one_question in self.test_questions:
            crud.create_question(
                question=one_question[0], acceptable_answers=one_question[1])

    def make_user_answers(self):
        """Make a PASS, FAIL and SKIP entry for one user"""
        crud.create_user_answer(user_id=9, question_id=9, answer_given='snitch')
        crud.create_user_answer(user_id=9, question_id=8, answer_given='snitch')
        crud.create_user_answer(user_id=9, question_id=7, answer_given='')

    def test_crud(self):
        self.make_users()
        self.assertEquals("Percy", crud.get_user_by_id(user_id=5).fname)
        self.assertEquals('fred@weasleyswizardingwheezes.com', crud.get_user_by_id(user_id=6).email)
        self.assertEquals("Charlie", crud.get_user_by_email(email='charlie@dragon_preserve.ro').fname)
        self.assertEquals("Arthur", crud.get_user_by_email(email='arthur@ministry_of_magic.gov').fname)
        self.assertTrue(crud.does_this_user_exist_already(email='arthur@ministry_of_magic.gov'))
        self.assertFalse(crud.does_this_user_exist_already(email='severus@death_eaters.org'))
        self.assertTrue(crud.does_the_password_match(email='arthur@ministry_of_magic.gov', password='test'))
        self.assertFalse(crud.does_the_password_match(email='arthur@ministry_of_magic.gov', password='rubber duck'))
        
        self.make_questions()
        self.assertEquals("Name a teacher.", crud.get_question_by_id(question_id=2).question)
        self.assertIn("snape", crud.get_question_by_id(question_id=2).acceptable_answers)
        self.assertIn(crud.get_one_right_answer(crud.get_question_by_id(question_id=2)), ['snape', 'mcgonigal'])
        possible_answers = crud.compile_possible_answers()
        self.assertIn('snitch', possible_answers)
        self.assertIn('draco', possible_answers)
        self.assertNotIn('horcrux', possible_answers)
        three_wrong_answers = crud.get_three_wrong_answers(
            question_instance=crud.get_question_by_id(question_id=2), 
            possible_answers=possible_answers)
        for wrong_answer in three_wrong_answers:
            self.assertNotIn(wrong_answer, ['snape', 'mcgonigal'])
        
        self.make_user_answers()
        self.assertEquals(50, crud.get_user_score(crud.get_user_by_id(user_id=9))["percent"])
        self.assertEquals(0, crud.get_user_score(crud.get_user_by_id(user_id=8))["percent"])
        self.assertIn('1 out of 3 correct.', crud.grade_all_answers())

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        # Test Data is purged at the end of each test:
        db.drop_all()


if __name__ == "__main__":
    unittest.main()
