"""User Answer operations for KFJC Trivia Robot."""

from datetime import datetime

from model import db, connect_to_db, UserAnswer
import common


def create_user_answer(user_instance, question_instance, answer_given):
    """Create and return a new user answer."""
    user_answer = UserAnswer(
        user_id=user_instance.user_id,
        question_id=question_instance.question_id,
        answer_given=answer_given,
        answer_correct=is_user_answer_correct(question_instance, answer_given),
        timestamp=datetime.now())

    db.session.add(user_answer)
    # Don't forget to call model.db.session.commit() when done adding items.

    return user_answer


def get_user_answers():
    """Return all user_answers."""

    return UserAnswer.query.all()


def get_one_users_answers(user_instance):
    """Return all user_answers for one user."""

    return UserAnswer.query.filter(UserAnswer.user_id == user_instance.user_id).all()


def is_user_answer_correct(question_instance, answer_given):
    """Return a boolean"""

    if answer_given:
        if answer_given in question_instance.acceptable_answers:
            return True
        else:
            return False
    else:
        return  # For the skipped question case.


def get_user_score(user_instance):
    """Return user play stats."""

    # TODO: Update the data model to include answer_correct with states:
    # true, false and null. Be careful about your handling because null
    # seems to behave false-y.

    passed = 0
    failed = 0
    skipped = 0
    num_questions = 0
    percent = 0.0

    users_answers = get_one_users_answers(user_instance)

    for user_answer_instance in users_answers:
        num_questions += 1
        if user_answer_instance.answer_correct is None:
            skipped += 1
        elif user_answer_instance.answer_correct is True:
            passed += 1
        elif user_answer_instance.answer_correct is False:
            failed += 1
        else:
            print("That's weird.")

    percent = common.percent_correct(passed_count=passed, failed_count=failed)

    user_score = {'passed': passed, 'failed': failed, 'skipped': skipped,
        'questions': num_questions, 'percent': percent}

    return user_score


def grade_all_answers():
    """Sanity check for get_user_score()."""

    user_answer_printout = []
    all_passed = 0
    all_failed = 0
    all_skipped = 0
    all_num_questions = 0
    all_percent = 0.0

    for user_answer_instance in get_user_answers():
        user_score = get_user_score(user_answer_instance)
        all_passed += user_score['passed']
        all_failed += user_score['failed']
        all_skipped += user_score['skipped']
        all_num_questions += user_score['questions']
        user_answer_printout.append(user_score)
        
    for dd in user_answer_printout:
        print(dd)
    
    all_percent = common.percent_correct(passed_count=all_passed, failed_count=all_failed)

    all_users_score = {'passed': all_passed, 'failed': all_failed, 'skipped': all_skipped,
        'questions': all_num_questions, 'percent': all_percent}

    return all_users_score

if __name__ == '__main__':
    """Will connect you to the database when you run user_answers.py interactively"""
    from server import app
    connect_to_db(app)
