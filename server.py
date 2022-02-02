"""Server for KFJC Trivia Robot app."""

from flask import (Flask, render_template, request, flash, session,
                   redirect)
from model import connect_to_db, db
from random import choice, choices, randint
import common
import users
import questions
import user_answers


from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "872tr87y23e9y120e[h1d"
app.jinja_env.undefined = StrictUndefined

praise = ["Aw, yeah!", "Oh, yeah!", "Sch-weet!", "Cool!", "Yay!", "Right!", "Correct!",
    "You're right!", "You are Correct!", "Awesome!", "You're a wiz!"]
consolation = ["Shucks", "Bad luck.", "Too bad.", "Better luck next time!", 
    "Awwww...", "Oh no!", "Sorry, wrong..."]
information = ["Here's what I found:", "I found these:", "Here's your answer:"]

current_user = None

def random_robot_image():
    """Give a path to a robot image."""
    robot_picture_idx = choice(range(1, 6))

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

    if game_on:
        next_question = questions.get_random_question()
        return render_template(
            'question.html',
            random_robot_img=random_robot_image(),
            question=next_question.question)
    else:
        # Send user to KFJC.org "Listen Now".
        return redirect('https://kfjc.org/player')


@app.route("/answer", methods = ["POST"])
def answer_question():
    """Take ."""

    record_answer = user_answers.create_user_answer(
        user_instance="", 
        question_instance="", 
        answer_given=request.form.get("answer"))
    db.session.commit()

    if record_answer.answer_correct:
        user_msg = choice(praise) + "\n\n" + choice(information)
    else:
        user_msg = choice(consolation) + "\n\n" + choice(information)

    return render_template(
        'answer.html',
        random_robot_img=random_robot_image(),
        user_msg=user_msg,
        display_answer=question_instance.acceptable_answers)



@app.route("/leaderboard")
def leaderboard():

    score_board = []

    for user_id in range(1, users.count_users()):
        user_instance = users.get_user_by_id(user_id=user_id)
        user_score = user_answers.get_user_score(user_instance=user_instance)
        user_percent = user_score['percent']
        score_board.append(f'{user_percent}%  {user_instance.fname}')
    
    score_board.sort(reverse=True)
    # TODO: Handle this later with a div, css and columns.

    user_msg = "You're in the KFJC Top40!" if (
        current_user == user_instance) else "Here's the KFJC Top40!"

    return render_template(
        'leaderboard.html',
        random_robot_img=random_robot_image(),
        table_range=min(40, len(score_board)),
        user_msg=user_msg,
        leaders=score_board,
        question="Play again?")
    

if __name__ == "__main__":
    connect_to_db(app)
    # DebugToolbarExtension(app)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = False

    app.run(host="0.0.0.0", debug=True)
