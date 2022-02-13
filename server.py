"""Server for KFJC Trivia Robot app."""

import os
import re
from flask import (Flask, render_template, request, flash, session,
                   redirect)
from model import connect_to_db, db
from random import choice
import users
import questions
import answers
from operator import itemgetter
import collections
import common

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
app.jinja_env.undefined = StrictUndefined

PRAISE_MSG = ["Aw, yeah!", "Oh, yeah!", "Sch-weet!", "Cool!", "Yay!", "Right!", "Correct!",
    "You're right!", "You are Correct!", "Awesome!", "You're a wiz!"]
CONSOLATION_MSG = ["Shucks", "Bad luck.", "Too bad.", "Better luck next time!", 
    "Awwww...", "Oh no!", "Sorry, wrong..."]
SKIP_MSG = ["Sorry you're not a fan of that one.", "I'll try to do better next time.",
    "No problem."]
INFO_MSG = ["Here's what I found:", "I found these:", "Here's your answer:"]
ROBOT_MSG = ["Robot loves you!", "Pretty good, meatbag!", "Well done, bag of mostly water!"]
TOP_N_USERS = 10  # Displayed on Leaderboard

def random_robot_image():
    """Give a path to a robot image."""
    
    robot_picture_idx = choice(range(1, 13))

    return f"static/img/robot{robot_picture_idx}.png"


@app.route("/")
def homepage():
    """Display homepage."""

    return render_template(
        'homepage.html', random_robot_img=random_robot_image())


@app.route("/play")
def shall_we_play():
    """Proceed with game or not."""

    game_on = request.args.get("game-on")  # Bool

    if game_on == 'true':
        return redirect('/question')
    else:
        # Send user to KFJC.org "Listen Now".
        return redirect('https://kfjc.org/player')


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""
    username = request.form["username"]
    password = request.form["password"]

    user_instance = users.get_user_by_username(username=username)

    if not user_instance:
        flash("No one with that email found.")
        return redirect("/")
    if users.does_password_match(
            plain_text_password=password,
            hashed_password=user_instance.hashed_password):
        session["user_id"] = user_instance.user_id
        return redirect("/question")
    else:
        flash("Oops, password didn't match.")
        return redirect("/")

@app.route('/create_account', methods=['POST'])
def create_account():
    """Create A new user."""
    username = request.form["username"]
    fname = request.form["fname"]
    password = request.form["password"]
    
    new_user = users.create_a_user(username, fname, password)

    if not new_user:
        flash("Oops, that username's taken.")
        return redirect("/")
    else:
        session["user_id"] = new_user.user_id
        return redirect("/question")

@app.route("/important")
def important():
    """Important info for logged in users."""
    #if "user_id" in session:
    #    return render_template("important.html")
    #
    #else:
    flash("Make an account to take a fun quiz.")
    return redirect("/")

@app.route("/logout")
def logout():
    """User must be logged in."""
    if "user_id" not in session:
        return redirect('/important')
    del session["user_id"]
    if "question_id" in session:
        del session["question_id"]
    flash("Logged Out.")
    return redirect("/")

@app.route("/question")
def ask_question():
    """Offer a question to user."""
    if "user_id" not in session:
        return redirect('/important')

    next_question = questions.get_unique_question(user_id=session["user_id"])
    if isinstance(next_question, str):  # TODO use try/except instead of returning 2 different data types.
        error_message = next_question
        flash(error_message)
        return redirect("/leaderboard")
    else:
        session["question_id"] = next_question.question_id
        answer_pile = questions.get_answer_pile(question_instance=next_question)

        return render_template(
            'question.html',
            random_robot_img=random_robot_image(),
            question=next_question.question,
            answer_a=answer_pile[0],
            answer_b=answer_pile[1],
            answer_c=answer_pile[2],
            answer_d=answer_pile[3])

@app.route("/answer", methods = ["POST"])
def answer_question():
    """Deal with response from user."""

    answer_given=request.form.get("q")

    user_id=session["user_id"]
    user_instance = users.get_user_by_id(user_id=user_id)

    question_instance = questions.get_question_by_id(
        question_id=session["question_id"])

    record_answer = answers.create_answer(
        user_instance=user_instance, 
        question_instance=question_instance, 
        answer_given=answer_given)
    db.session.commit()

    if answer_given == "SKIP":  # That's a skip.
        return redirect('/question')

    if record_answer.answer_correct:
        user_msg = choice(PRAISE_MSG) + "\n\n" + choice(INFO_MSG)
        answer_correct = True
    else:
        user_msg = choice(CONSOLATION_MSG) + "\n\n" + choice(INFO_MSG)
        answer_correct = False

    question_instance = questions.get_question_by_id(
        question_id=session["question_id"])

    if question_instance.question_type == "most_shows":
        right_answer = collections.OrderedDict(reversed(sorted(question_instance.acceptable_answers["display_all_answers"].items())))
        table_display = True
    elif question_instance.question_type == "earliest_show":
        # dj_first_show = common.make_date_pretty(dj_info_deck[dj_id]['first_show'].strftime('%Y-%m-%d %H:%M:%S'))
        right_answer = collections.OrderedDict(sorted(question_instance.acceptable_answers["display_all_answers"].items()))
        right_answer_pretty = collections.OrderedDict()
        for key in right_answer:
            right_answer_pretty[common.make_date_pretty(key)] = right_answer[key]
        table_display = True
        right_answer = right_answer_pretty
    else:
        right_answer = question_instance.acceptable_answers["display_answer"]
        table_display = False

    return render_template(
        'answer.html',
        random_robot_img=random_robot_image(),
        user_msg=user_msg,
        answer_correct=answer_correct,
        restate_the_question=question_instance.acceptable_answers["rephrase_the_question"],
        table_display=table_display,
        right_answer=right_answer)
        

@app.route("/infopage")
def infopage():
    return render_template(
        'infopage.html',
        random_robot_img=random_robot_image())

@app.route("/score")
def myscore():
    if "user_id" not in session:
        return redirect('/important')

    user_instance=users.get_user_by_id(user_id=session["user_id"])

    user_score = answers.get_user_score(user_instance=user_instance)

    return render_template(
        'score.html',
        random_robot_img=random_robot_image(),
        fname=user_instance.fname,
        user_score=user_score)


@app.route("/leaderboard")
def leaderboard():
    if "user_id" not in session:
        return redirect('/important')

    score_board = []

    for user_instance in users.get_users():
        user_score = answers.get_user_score(user_instance=user_instance)
        user_percent = user_score['percent']
        score_board.append([user_instance.user_id, user_percent, f"{user_percent}% {user_instance.fname}"])
    
    score_board.sort(key=itemgetter(1), reverse=True)

    table_range=min(TOP_N_USERS, len(score_board))
    if session["user_id"] in [f[0] for f in score_board[:table_range]]:
        user_msg = "You're in the KFJC Top10!"
    else:
        user_msg = "Our Top10 Leaders:"

    return render_template(
        'leaderboard.html',
        random_robot_img=random_robot_image(),
        robot_msg=choice(ROBOT_MSG),
        table_range=table_range,
        current_user = session["user_id"],
        user_msg=user_msg,
        leaders=score_board)
    

if __name__ == "__main__":
    connect_to_db(app)
    # DebugToolbarExtension(app)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = False

    app.run(host="0.0.0.0", debug=True)
