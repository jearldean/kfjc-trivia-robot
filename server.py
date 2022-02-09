"""Server for KFJC Trivia Robot app."""

from flask import (Flask, render_template, request, flash, session,
                   redirect)
from model import connect_to_db, db
from random import choice
import users
import questions
import answers

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "872tr87y23e9y120e[h1d"
app.jinja_env.undefined = StrictUndefined

praise = ["Aw, yeah!", "Oh, yeah!", "Sch-weet!", "Cool!", "Yay!", "Right!", "Correct!",
    "You're right!", "You are Correct!", "Awesome!", "You're a wiz!"]
consolation = ["Shucks", "Bad luck.", "Too bad.", "Better luck next time!", 
    "Awwww...", "Oh no!", "Sorry, wrong..."]
skipped = ["Sorry you're not a fan of that one.", "I'll try to do better next time.",
    "No problem."]
information = ["Here's what I found:", "I found these:", "Here's your answer:"]
robot_messages = ["Robot loves you!", "Pretty good, meatbag!", "Well done, bag of mostly water!"]

current_user = None
current_question = None

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
    if "username" in session:
        return render_template("important.html")

    else:
        flash("You must be logged in to view the important page")
        return redirect("/login")

@app.route("/logout")
def logout():
    """User must be logged in."""
    del session["user_id"]
    del session["question_id"]
    flash("Logged Out.")
    return redirect("/login")

@app.route("/question")
def ask_question():
    next_question = questions.get_unique_question(user_id=session["user_id"])
    if isinstance(next_question, str):
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
    """Take ."""

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
        user_msg = choice(praise) + "\n\n" + choice(information)
    else:
        user_msg = choice(consolation) + "\n\n" + choice(information)

    question_instance = questions.get_question_by_id(
        question_id=session["question_id"])

    """
    acceptable_answers = {
        "calculate_answer": isoformat_date_time_str,
        "answer_choice": common.make_date_pretty(isoformat_date_time_str),
        "display_answer": display_answer}
    """

    return render_template(
        'answer.html',
        random_robot_img=random_robot_image(),
        user_msg=user_msg,
        restate_the_question=question_instance.acceptable_answers["display_answer"],
        right_answer=question_instance.acceptable_answers["answer_choice"])
        

@app.route("/infopage")
def infopage():
    return render_template(
        'infopage.html',
        random_robot_img=random_robot_image())

@app.route("/score")
def myscore():

    user_instance=users.get_user_by_id(user_id=session["user_id"])

    user_score = answers.get_user_score(user_instance=user_instance)

    return render_template(
        'score.html',
        random_robot_img=random_robot_image(),
        fname=user_instance.fname,
        user_score=user_score)


@app.route("/leaderboard")
def leaderboard():

    score_board = []

    user_ids = [one_user.user_id for one_user in users.get_users()]
    for user_id in user_ids:
        user_instance = users.get_user_by_id(user_id=user_id)
        user_score = answers.get_user_score(user_instance=user_instance)
        user_percent = user_score['percent']
        score_board.append(f'{user_percent}%  {user_instance.fname}')
    
    score_board.sort(reverse=True)
    # TODO: Handle this later with a div, css and columns.

    #user_msg = "You're in the KFJC Top40!" if (
    #    current_user == user_instance) else "Here's the KFJC Top40 Users!"
    # user_id=session["user_id"]
    user_msg = "Here are the Top Ten KFJC Trivia Robot Players!"

    return render_template(
        'leaderboard.html',
        random_robot_img=random_robot_image(),
        robot_msg=choice(robot_messages),
        table_range=min(10, len(score_board)),
        user_msg=user_msg,
        leaders=score_board,
        question="Play again?")
    

if __name__ == "__main__":
    connect_to_db(app)
    # DebugToolbarExtension(app)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = False

    app.run(host="0.0.0.0", debug=True)
