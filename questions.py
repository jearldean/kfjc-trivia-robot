"""Question operations for KFJC Trivia Robot."""

from model import db, connect_to_db, UserAnswer, Question
from random import choice, choices


def create_question(question, acceptable_answers):
    """Create and return a new question."""

    question = Question(question=question,
                        acceptable_answers=acceptable_answers)

    db.session.add(question)
    # Don't forget to call model.db.session.commit() when done adding items.

    return question


def get_questions():
    """Get all questions."""

    return Question.query.all()

def get_question_by_id(question_id):
    """Return one question."""

    return Question.query.get(question_id)


def get_random_question():
    """Get a random question."""

    # TODO: Eliminate User's Already-Answered Questions from the reply

    num_questions = Question.query.count()
    random_pk = choice(range(1, num_questions+1))
    return Question.query.get(random_pk)


def get_unique_question(user_id):
    """Make sure the user has never been asked this question before."""

    return Question.query.filter(Question.question_id.not_in(
        UserAnswer.query.filter(UserAnswer.user_id == user_id).all()))


def get_one_right_answer(question_instance):
    """Get an acceptable_answer for multiple choice question."""

    return choice(question_instance.acceptable_answers)


def get_three_wrong_answers(question_instance, possible_answers):
    """Get three unacceptable_answers for multiple choice question."""

    for correct_answer in question_instance.acceptable_answers:
        possible_answers.remove(correct_answer)
    return choices(possible_answers, k=3)


def compile_possible_answers():
    """TODO: This is not the final way I want to do this. 
    Should use SQLAlchemy. Just getting it working using loops for now."""
    possible_answers = []

    for question_instance in get_questions():
        possible_answers += question_instance.acceptable_answers
    return possible_answers



if __name__ == '__main__':
    """Will connect you to the database when you run questions.py interactively"""
    from server import app
    connect_to_db(app)
