"""Server for KFJC Trivia Robot app."""

import os
from random import choice
from flask import (Flask, render_template, request, flash, session, redirect)
from jinja2 import StrictUndefined
from operator import itemgetter

from model import connect_to_db, db
import playlists
import playlist_tracks
import users
import common
import users
import questions
import answers

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
app.jinja_env.undefined = StrictUndefined

TOP_N_USERS = 10  # Displayed on Leaderboard
ROBOT_MSG = ["Robot loves you!", "Pretty good, meatbag!", "Well done, bag of mostly water!"]

# -=-=-=-=-=-=-=-=-=-=-=- Routes -=-=-=-=-=-=-=-=-=-=-=-

@app.route("/")
def homepage():
    """Display homepage."""

    return render_template(
        'homepage.html', random_robot_img=random_robot_image(),
        greeting = assemble_greeting())

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

@app.route("/question")
def ask_question():
    """Offer a question to user."""
    if "user_id" not in session:
        return redirect('/important')

    next_question = questions.get_unique_question(user_id=session["user_id"])

    if not next_question:
        flash("You've answered all the questions! I'm exhausted.")
        return redirect("/leaderboard")
    else:
        session["question_id"] = next_question.question_id

        return render_template(
            'question.html',
            random_robot_img=random_robot_image(),
            question=next_question.ask_question,
            shuffled_answers = next_question.wrong_answers[0])

@app.route("/ask")
def user_asks():
    """Offer a question to user."""
    if "user_id" not in session:
        return redirect('/important')

    return render_template(
        'ask.html',
        random_robot_img=random_robot_image())

@app.route("/answer", methods = ["POST"])
def answer_question():
    """TODO"""

    answer_given=request.form.get("q")
    user = users.get_user_by_id(user_id=session["user_id"])
    question = questions.get_question_by_id(question_id=session["question_id"])

    answer = answers.create_answer(
        user_instance=user, 
        question_instance=question, 
        answer_given=answer_given)
    db.session.commit()

    if answer_given == "SKIP":  # That's a skip.
        return redirect('/question')

    user_msg, restate_the_question, right_answer = (
        answers.handle_incoming_answer(question=question, answer=answer))

    return render_template(
        'answer.html',
        random_robot_img=random_robot_image(),
        user_msg=user_msg,
        answer_correct=answer.answer_correct,
        restate_the_question=restate_the_question,
        right_answer=right_answer)

@app.route("/leaderboard")
def leaderboard():
    """TODO: Can leaderboard be rest api?
    TODO:  Can we use sql alchemy processing to get the leaders?"""

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

# -=-=-=-=-=-=-=-=-=-=-=- REST API -=-=-=-=-=-=-=-=-=-=-=-


# -=-=-=-=-=-=-=-=-=-=-=- Python -=-=-=-=-=-=-=-=-=-=-=-

def random_robot_image():
    """Give a path to a robot image."""
    
    robot_picture_idx = choice(range(1, 13))

    return f"static/img/robot{robot_picture_idx}.png"

def assemble_greeting():
    """Gather stats for to make a compelling reason to take a database quiz."""

    first_and_last_show = playlists.first_show_last_show()
    first_show_in_db = common.make_date_pretty(first_and_last_show[0])
    duration = common.minutes_to_years(
        ((first_and_last_show[1] - first_and_last_show[0]).total_seconds())/60)
    count_all_shows = common.format_an_int_with_commas(playlists.how_many_shows())
    count_prolific_djs = common.format_an_int_with_commas(playlists.how_many_djs())
    count_playlist_tracks = common.format_an_int_with_commas(playlist_tracks.how_many_tracks())

    greeting = (
        f"KFJC has a database going back to {first_show_in_db} "
        f"that contains {count_all_shows} shows by {count_prolific_djs} DJs. "
        f"They've played {count_playlist_tracks} songs in {duration}! "
        f"Wanna play a trivia game with me?")
    return greeting


if __name__ == "__main__":
    connect_to_db(app)
    # DebugToolbarExtension(app)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = False

    app.run(host="0.0.0.0", debug=True)
