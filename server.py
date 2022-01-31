"""Server for KFJC Trivia Robot app."""

from flask import (Flask, render_template, request, flash, session,
                   redirect)
from random import choice
from model import connect_to_db

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "872tr87y23e9y120e[h1d"
app.jinja_env.undefined = StrictUndefined

possible_answers = [
    'expelliarmus', 'alohamora', 'snape', 'mcgonigal', 'dumbledore', 'harry',
    'ron', 'hermione', 'draco', 'severus', 'salizar', 'cedric', 'luna', 'cho',
    'nimbus 2000', 'cleansweep 7', 'silver arrow', 'snitch', 'bludger',
    'quaffle']
praise = ["Aw, yeah!", "Oh, yeah!", "Sch-weet!", "Cool!", "Yay!", "Right!", "Correct!",
    "You're right!", "You are Correct!", "Awesome!", "You're a wiz!"]
consolation = ["Shucks", "Bad luck.", "Too bad.", "Better luck next time!", 
    "Awwww...", "Oh no!", "Sorry, wrong..."]
# FUTURE: information = ["Here's what I found:", "I found these:", "Here's your answer:"]

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

    response = request.args.get("game-on")

    if response == "yes":  # TO DO: Maybe a boolean here?
        # next_question = question_maker.formulate_question()
        next_question = crud.ran 
        return render_template(
            'question.html', random_robot_img=random_robot_image(),
            question=next_question)
    else:
        # Send user to KFJC.org "Listen Now".
        return redirect('https://kfjc.org/player')


@app.route("/answer") # , methods = ["POST"]
def answer_question():
    """Take ."""

    response = request.args.get("answer")

    if response == "yes":  # TO DO: Maybe a boolean here?
        # next_question = question_maker.formulate_question()
        question_instance = crud.get_random_question()
        one_right_answer = crud.get_one_right_answer(question_instance=question_instance)
        three_wrong_answers = crud.get_three_wrong_answers(
            question_instance=question_instance,
            possible_answers=possible_answers)
        return render_template(
            'question.html', random_robot_img=random_robot_image(),
            question=next_question)
    else:
        # Send user to KFJC.org "Listen Now".
        return redirect('https://kfjc.org/player')


if __name__ == "__main__":
    connect_to_db(app)
    # DebugToolbarExtension(app)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = False

    app.run(host="0.0.0.0", debug=True)
