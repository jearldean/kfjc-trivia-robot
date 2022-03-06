"""Answer operations for KFJC Trivia Robot."""

from datetime import datetime
from random import choice

from model import db, connect_to_db, Answer


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
    """TODO"""
    if answer.answer_correct:
        user_msg = choice(PRAISE_MSG) + "\n\n" + choice(INFO_MSG)
    else:
        user_msg = choice(CONSOLATION_MSG) + "\n\n" + choice(INFO_MSG)
    return user_msg

def is_answer_correct(question_instance, answer_given):
    """Return a boolean"""

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
    """Return all user_answers for one user.
    
    for i in answers:
        print(i.answer_given)
        print(i.answer_correct)
    """

    return Answer.query.filter(Answer.user_id == user_id).all()

def get_user_score(user_id):
    """Return user play stats.
    
    NICE-TO-HAVE: get counts using SQL.
    NICE-TO-HAVE: return a named tuple. """
    passed=0
    failed=0
    skipped=0
    for jj in get_one_users_answers(user_id=user_id):
        if jj.answer_correct is True:
            passed += 1
        elif jj.answer_correct is False:
            failed += 1
        elif jj.answer_correct is None:
            skipped += 1
    questions = passed + failed + skipped
    percent = percent_correct(passed_count=passed, failed_count=failed)
    scores = {
        'passed': passed, 'failed': failed, 'skipped': skipped,
        'questions': questions, 'percent': percent}

    return scores


if __name__ == '__main__':
    """Will connect you to the database when you run answers.py interactively"""
    from server import app
    connect_to_db(app)

    import doctest
    doctest.testmod()  # python3 answers.py -v