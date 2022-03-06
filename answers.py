"""Answer operations for KFJC Trivia Robot."""

from datetime import datetime
from random import choice
from operator import itemgetter

from model import db, connect_to_db, Answer
import users
import common


PRAISE_MSG = ["Aw, yeah!", "Oh, yeah!", "Sch-weet!", "Cool!", "Yay!", "Right!", "Correct!",
    "You're right!", "You are Correct!", "Awesome!", "You're a wiz!"]
CONSOLATION_MSG = ["Shucks", "Bad luck.", "Too bad.", "Better luck next time!", 
    "Awwww...", "Oh no!", "Sorry, wrong...", "So close!"]
INFO_MSG = [
    "Here's what I found:", "I found these:", "Here's your answer:",
    "My databanks say:", "I computed these results:"]


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

def get_user_msg(answer):
    """Craft a message for the user about their answer."""
    if answer.answer_correct:
        user_msg = choice(PRAISE_MSG) + "\n\n" + choice(INFO_MSG)
    else:
        user_msg = choice(CONSOLATION_MSG) + "\n\n" + choice(INFO_MSG)
    return user_msg

def is_answer_correct(question_instance, answer_given):
    """Return a boolean."""

    if answer_given == "SKIP":
        return  # None, for the skipped question case.
    else:
        if answer_given == question_instance.acceptable_answer:
            return True
        return False  # If we didn't hit by now, it's wrong.

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

def get_one_users_answers(user_id):
    """Return all user_answers for one user."""

    return Answer.query.filter(Answer.user_id == user_id).all()

def get_user_score(user_id):
    """Return user play stats."""

    passed = Answer.query.filter(
        Answer.user_id == user_id, Answer.answer_correct == True).count()
    failed = Answer.query.filter(
        Answer.user_id == user_id, Answer.answer_correct == False).count()
    skipped = Answer.query.filter(
        Answer.user_id == user_id, Answer.answer_correct == None).count()
    questions = passed + failed + skipped
    percent = percent_correct(passed_count=passed, failed_count=failed)
    scores = {
        'passed': passed, 'failed': failed, 'skipped': skipped,
        'questions': questions, 'percent': percent}
    return common.convert_dict_to_named_tuple(scores)

def compile_leaderboard():
    """Return stats for all users."""

    score_board = []

    for user in users.get_users():
        user_id=user.user_id
        user_score_named_tuple = get_user_score(user_id=user_id)
        user_percent = user_score_named_tuple.percent
        score_board.append(
            [user_id, user_percent, f"{user_percent}% {user.fname}"])
    
    score_board.sort(key=itemgetter(1), reverse=True)
    
    return score_board



if __name__ == '__main__':
    """Will connect you to the database when you run answers.py interactively"""
    from server import app
    connect_to_db(app)

    import doctest
    doctest.testmod()  # python3 answers.py -v