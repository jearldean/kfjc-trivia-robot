"""CRUD operations for KFJC Trivia Robot."""

from model import db, User, UserAnswer, Question, connect_to_db
from datetime import datetime
from random import choice, choices

# USER Functions:


def create_user(email, fname, password, salt):
    """Create and return a new user."""

    user = User(email=email, fname=fname, password=password, salt=salt)

    db.session.add(user)
    db.session.commit()

    return user


def get_users():
    """Return all users."""

    return User.query.all()


def get_user_by_id(user_id):
    """Return a user by primary key."""

    return User.query.get(user_id)


def get_user_by_email(email):
    """Return a user by email."""

    return User.query.filter(User.email == email).first()


def does_this_user_exist_already(email):
    """Return a boolean we can use for the if-statement in server.py."""

    if get_user_by_email(email):
        return True
    else:
        return False


def does_the_password_match(email, password):
    """Return a boolean we can use for the if-statement in server.py."""

    if User.query.filter(User.email == email, User.password == password).first():
        return True
    else:
        return False

# QUESTION Functions:


def create_question(question, acceptable_answers):
    """Create and return a new question."""

    question = Question(question=question,
                        acceptable_answers=acceptable_answers)

    db.session.add(question)
    db.session.commit()

    return question


def get_questions():
    """Get all questions."""

    return Question.query.all()


def get_random_question():
    """Get a random question."""

    return choice(get_questions())


def get_unique_question(user_id):
    """Make sure the user has never been asked this question before."""

    return Question.query.filter(Question.question_id.not_in(UserAnswer.query.filter(UserAnswer.user_id == user_id).all()))


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


def get_question_by_id(question_id):
    """Return one question."""

    return Question.query.get(question_id)

# USER ANSWER Functions:


def create_user_answer(user_id, question_id, answer_given):
    """Create and return a new user answer."""
    timestamp = datetime.now()
    user_answer = UserAnswer(user_id=user_id, question_id=question_id,
                             answer_given=answer_given, timestamp=timestamp)

    db.session.add(user_answer)
    db.session.commit()

    return user_answer


def get_user_answers():
    """Return all user_answers."""

    return UserAnswer.query.all()


def get_one_users_answers(user_instance):
    """Return all user_answers for one user."""

    return UserAnswer.query.filter(
        UserAnswer.user_id == user_instance.user_id).all()


def is_user_answer_correct(question_instance, user_answer_instance):
    """Return a boolean for the if-statement in crud.evaluate_answer()."""

    if UserAnswer.query.filter(
            user_answer_instance.question_id == question_instance.question_id,
            user_answer_instance.answer_given in question_instance.acceptable_answers).first():
        return True
    else:
        return False


def get_user_score(user_instance):
    """Return user play stats."""

    passed = 0
    failed = 0
    skipped = 0
    questions = 0
    percent = 0.0

    users_answers = get_one_users_answers(user_instance)

    for user_answer_instance in users_answers:
        questions += 1
        question_instance = get_question_by_id(
            user_answer_instance.question_id)
        if user_answer_instance.answer_given:
            correct_answer = is_user_answer_correct(
                question_instance, user_answer_instance)
            if correct_answer:
                passed += 1
            else:
                failed += 1
        else:  # NULL
            skipped += 1
    try:
        percent = float(passed) * 100 / (passed + failed)
    except ZeroDivisionError:
        percent = 0.0

    return {'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'questions': questions,
            'percent': percent}


def grade_all_answers():
    """Sanity check for is_user_answer_correct()."""

    total_answers = 0
    total_correct_answers = 0

    all_user_answer_instances = get_user_answers()
    for user_answer_instance in all_user_answer_instances:
        total_answers += 1
        question_instance = get_question_by_id(
            user_answer_instance.question_id)
        correct_answer = is_user_answer_correct(
            question_instance, user_answer_instance)
        if correct_answer:
            total_correct_answers += 1
    return f"\n\n{total_correct_answers} out of {total_answers} correct."


if __name__ == '__main__':
    """Will connect you to the database when you run crud.py interactively"""
    from server import app
    connect_to_db(app)
