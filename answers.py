"""Answer operations for KFJC Trivia Robot."""

from datetime import datetime
from sqlalchemy import func
from random import choice

from model import db, connect_to_db, Answer


PRAISE_MSG = ["Aw, yeah!", "Oh, yeah!", "Sch-weet!", "Cool!", "Yay!", "Right!", "Correct!",
    "You're right!", "You are Correct!", "Awesome!", "You're a wiz!"]
CONSOLATION_MSG = ["Shucks", "Bad luck.", "Too bad.", "Better luck next time!", 
    "Awwww...", "Oh no!", "Sorry, wrong..."]
INFO_MSG = ["Here's what I found:", "I found these:", "Here's your answer:"]


def create_answer(user_instance, question_instance, answer_given):
    """Create and return a new answer."""

    user_answer = Answer(
        user_id=user_instance.user_id,
        question_id=question_instance.question_id,
        answer_given=answer_given,
        answer_correct=is_answer_correct(question_instance, answer_given),
        timestamp=datetime.now())

    db.session.add(user_answer)
    # Don't forget to call model.db.session.commit() when done adding items.

    return user_answer


def get_one_users_answers(user_instance):
    """Return all user_answers for one user."""

    return Answer.query.filter(Answer.user_id == user_instance.user_id).all()

def handle_incoming_answer(question, answer):
    """TODO"""
    if answer.answer_correct:
        user_msg = choice(PRAISE_MSG) + "\n\n" + choice(INFO_MSG)
    else:
        user_msg = choice(CONSOLATION_MSG) + "\n\n" + choice(INFO_MSG)
    restate_the_question = question.present_answer
    the_right_answer = question.acceptable_answers[0]
    display_answers = question.wrong_answers[1]
    return user_msg, restate_the_question, the_right_answer, display_answers


def is_answer_correct(question_instance, answer_given):
    """Return a boolean"""

    if answer_given == "SKIP":
        return  # For the skipped question case.
    else:
        if answer_given in question_instance.acceptable_answers:
            return True
        return False  # If we didn't hit by now, it's wrong.


def get_user_score(user_instance):
    """Return user play stats."""

    passed = 0
    failed = 0
    skipped = 0
    num_questions = 0
    percent = 0.0

    users_answers = get_one_users_answers(user_instance)

    """ TODO   MAKE a solution that uses more sql alchemy:
    a = db.session.query(func.count(Answer.answer_correct)).group_by(
        Answer.answer_correct).all()
    print(a)"""

    for user_answer_instance in users_answers:
        num_questions += 1
        if user_answer_instance.answer_correct is None:
            skipped += 1  # Handle this case first. 
        elif user_answer_instance.answer_correct is True:
            passed += 1
        elif user_answer_instance.answer_correct is False:
            failed += 1
        else:
            print("That's weird.")

    percent = percent_correct(passed_count=passed, failed_count=failed)

    user_score = {'passed': passed, 'failed': failed, 'skipped': skipped,
        'questions': num_questions, 'percent': percent}

    return user_score


def percent_correct(passed_count, failed_count):
    """For scorekeeping, leaderboards.
    
    >>> percent_correct(0, 0)
    0.0
    >>> percent_correct(20, 80)
    20.0
    """

    try:
        percent = round(float(passed_count) * 100 / (passed_count + failed_count), 1)
    except ZeroDivisionError:
        percent = 0.0
    return percent


if __name__ == '__main__':
    """Will connect you to the database when you run answers.py interactively"""
    from server import app
    connect_to_db(app)
