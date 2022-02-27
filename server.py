"""Server for KFJC Trivia Robot app."""

import os
from random import choice
from flask import (Flask, render_template, request, flash, session, redirect, jsonify)
from jinja2 import StrictUndefined
from operator import itemgetter
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow

from model import connect_to_db, db, Playlist
import playlists
import playlist_tracks
import tracks
import users
import questions
import answers
import common

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
app.jinja_env.undefined = StrictUndefined
api = Api(app)
ma = Marshmallow(app)

TOP_N_USERS = 10  # Displayed on Leaderboard
ROBOT_MSG = ["Robot loves you!", "Pretty good, meatbag!", "Well done, bag of mostly water!"]

# -=-=-=-=-=-=-=-=-=-=-=- Routes -=-=-=-=-=-=-=-=-=-=-=-

@app.route("/")
def homepage():
    """Display homepage."""

    return render_template(
        'homepage.html', random_robot_img=random_robot_image(),
        greeting = assemble_greeting())

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

    dj_id=request.args.get("dj_id")
    
    dj_selected = int(dj_id)
    
    if not dj_selected:
        dj_selected = 177
    dj_stat = assemble_dj_stat(dj_id=dj_selected)

    print(dj_stat)
    
    #url = "/dj_stats"
    #from_the_rest_api = requests.get(url)
    #dj_dump_json = from_the_rest_api.text
    #dj_dump = json.loads(dj_dump_json)

    #return render_template(
    #    'ask.html',
    #    random_robot_img=random_robot_image(),
    #    dj_dump=dj_dump)


    return render_template(
        'ajax.html',
        random_robot_img=random_robot_image(),
        dj_list = session["dj_list"],
        #dj_dict=session["dj_dict"],
        #dj_selected=dj_id,
        dj_stat=dj_stat)

@app.route('/ajax', methods=['GET'])
def profile():
    """Return results from profile form."""

    profile_pack = {}
    profile_pack['name'] = request.json.get('name')
    profile_pack['age'] = request.json.get('age')
    profile_pack['occupation'] = request.json.get('occupation')
    profile_pack['salary'] = request.json.get('salary')
    profile_pack['education'] = request.json.get('education')
    profile_pack['state'] = request.json.get('state')
    profile_pack['interests'] = request.json.get('interests')
    profile_pack['garden'] = request.json.get('garden')
    profile_pack['tv'] = request.json.get('tv')

    return jsonify(profile_pack)


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

    user_msg, restate_the_question, the_right_answer, display_answers = (
        answers.handle_incoming_answer(question=question, answer=answer))

    return render_template(
        'answer.html',
        random_robot_img=random_robot_image(),
        user_msg=user_msg,
        answer_correct=answer.answer_correct,
        restate_the_question=restate_the_question,
        the_right_answer=the_right_answer,
        display_answers=display_answers)

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

def retrieve_dj_stats_only_once():
    djs_alphabetically = playlists.get_djs_alphabetically()
    dj_dict = {}
    dj_list = []
    for zz in djs_alphabetically:
        air_name = zz[0]
        dj_id = int(zz[1])
        showcount = common.format_an_int_with_commas(zz[2])
        firstshow = common.make_date_pretty(zz[3])
        lastshow = common.make_date_pretty(zz[4])
        # air_name, dj_id, showcount, firstshow, lastshow
        dj_dict[dj_id] = {
            'air_name': air_name,
            'showcount': showcount,
            'firstshow': firstshow,
            'lastshow': lastshow}
        dj_list.append([air_name, dj_id, showcount, firstshow, lastshow])
    session["dj_dict"] = dj_dict
    session["dj_list"] = dj_list
    #print(session["dj_dict"][177])
    #print(session["dj_list"][1])

def assemble_dj_stat(dj_id):
    if "dj_dict" not in session:
        retrieve_dj_stats_only_once()
    air_name = session["dj_dict"][dj_id]['air_name']
    the_right_apostrophe = common.the_right_apostrophe(air_name=air_name)
    showcount = session["dj_dict"][dj_id]['showcount']
    firstshow = session["dj_dict"][dj_id]['firstshow']
    lastshow = session["dj_dict"][dj_id]['lastshow']
    return (
        f"{air_name}{the_right_apostrophe} first show was on {firstshow}, "
        f"their last show was on {lastshow} and they have done {showcount} shows!")

# -=-=-=-=-=-=-=-=-=-=-=- REST API: Playlists -=-=-=-=-=-=-=-=-=-=-=-

class PlaylistSchema(ma.Schema):
    class Meta:
        fields = ("id_", "kfjc_playlist_id", "dj_id", "air_name", "start_time", "end_time")

playlist_schema = PlaylistSchema()
playlists_schema = PlaylistSchema(many=True)

class PlaylistListResource(Resource):
    def get(self):
        playlists = Playlist.query.all()
        return playlist_schema.dump(playlists)

api.add_resource(PlaylistListResource, '/playlists')

class PlaylistResource(Resource):
    def get(self, id_):
        playlist = Playlist.query.get_or_404(id_)
        return playlist_schema.dump(playlist)

api.add_resource(PlaylistResource, '/playlists/<int:id_>')
# api.add_resource(PlaylistResource, '/playlists/<int:kfjc_playlist_id>')

# -=-=-=-=-=-=-=-=-=-=-=- REST API: DJ Favorites -=-=-=-=-=-=-=-=-=-=-=-

class DJFavoritesSchema(ma.Schema):
    class Meta:
        fields = ("dj_id", "artist", "plays")

one_dj_favorites_schema = DJFavoritesSchema(many=True)

class DJFavoritesResource(Resource):
    def get(self, dj_id):
        favorites = playlist_tracks.djs_favorite(dj_id=dj_id)
        return one_dj_favorites_schema.dump(favorites)

api.add_resource(DJFavoritesResource, '/dj_favorites/<int:dj_id>')

# -=-=-=-=-=-=-=-=-=-=-=- REST API: Last Played -=-=-=-=-=-=-=-=-=-=-=-

class LastPlayedSchema(ma.Schema):
    class Meta:
        fields = ("air_name", "artist", "album_title", "track_title", "time_played")

last_played_schema = LastPlayedSchema(many=True)

class LastPlayedByArtist(Resource):
    def get(self, artist):
        last_time_played = playlist_tracks.last_time_played(artist=artist)
        return last_played_schema.dump(last_time_played)

class LastPlayedByAlbum(Resource):
    def get(self, album):
        last_time_played = playlist_tracks.last_time_played(album=album)
        return last_played_schema.dump(last_time_played)

class LastPlayedByTrack(Resource):
    def get(self, track):
        last_time_played = playlist_tracks.last_time_played(track=track)
        return last_played_schema.dump(last_time_played)

api.add_resource(LastPlayedByArtist, '/last_played/artist=<string:artist>')
api.add_resource(LastPlayedByAlbum, '/last_played/album=<string:album>')
api.add_resource(LastPlayedByTrack, '/last_played/track=<string:track>')


# -=-=-=-=-=-=-=-=-=-=-=- REST API: Top Ten -=-=-=-=-=-=-=-=-=-=-=-

class TopTenSchema(ma.Schema):
    class Meta:
        fields = ("plays", "artist", "album_title", "track_title")

top_n_artist_schema = TopTenSchema(many=True)

class TopTen(Resource):
    def get(self, start_date, end_date, order_by='track', top=10):
        if order_by in ['artist', 'artists']:
            top_10 = playlist_tracks.get_top10_artists(start_date, end_date, n=top)
        if order_by in ['album', 'albums']:
            top_10 = playlist_tracks.get_top10_albums(start_date, end_date, n=top)
        else:    # order_by in ['track', 'tracks']:
            top_10 = playlist_tracks.get_top10_tracks(start_date, end_date, n=top)

        return top_n_artist_schema.dump(top_10)

api.add_resource(TopTen, '/top_artists/top=<int:top>&start_date=<string:start_date>&end_date=<string:end_date>')

# -=-=-=-=-=-=-=-=-=-=-=- REST API: DJ Stats -=-=-=-=-=-=-=-=-=-=-=-
# http://0.0.0.0:5000/dj_stats/order_by=dj_id&reverse=1
class DJStatsSchema(ma.Schema):
    class Meta:
        fields = ("air_name", "dj_id", "showcount", "firstshow", "lastshow")

dj_stats_schema = DJStatsSchema(many=True)

class DJStatsNoArgs(Resource):
    def get(self):
        dj_stats = playlists.get_djs_alphabetically()
        #return dj_stats_schema.dump(dj_stats)
        return dj_stats_schema.jsonify(dj_stats)

class DJStats(Resource):
    def get(self, order_by=None, reverse=0):
        # Use 0, 1 for reverse
        if order_by in ['dj_id', 'id']:
            dj_stats = playlists.get_djs_by_dj_id(reverse=reverse)
        elif order_by in ['first_show', 'firstshow']:
            dj_stats = playlists.get_djs_by_first_show(reverse=reverse)
        elif order_by in ['last_show', 'lastshow']:
            dj_stats = playlists.get_djs_by_last_show(reverse=reverse)
        elif order_by in ['show_count', 'showcount', 'shows', 'playlists']:
            dj_stats = playlists.get_djs_by_show_count(reverse=reverse)
        else:
            dj_stats = playlists.get_djs_alphabetically(reverse=reverse)
        #return dj_stats_schema.dump(dj_stats)
        #return user_asks(dj_dump=dj_stats_schema.dump(dj_stats))
        # return dj_stats_schema.jsonify(dj_stats)
        return dj_stats_schema.jsonify(dj_stats)

api.add_resource(DJStats, '/dj_stats/order_by=<string:order_by>&reverse=<int:reverse>')
api.add_resource(DJStatsNoArgs, '/dj_stats')
# air_name, first_show, last_show and show_count

# -=-=-=-=-=-=-=-=-=-=-=- REST API: Album Tracks -=-=-=-=-=-=-=-=-=-=-=-
# http://0.0.0.0:5000/album_tracks/303
class AlbumTracksSchema(ma.Schema):
    class Meta:
        fields = ("indx", "title", "artist")

album_tracks_schema = AlbumTracksSchema(many=True)

class AlbumTracks(Resource):
    def get(self, kfjc_album_id):
        album_tracks = tracks.get_tracks_by_kfjc_album_id(kfjc_album_id)
        return album_tracks_schema.dump(album_tracks)

api.add_resource(AlbumTracks, '/album_tracks/<int:kfjc_album_id>')

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

if __name__ == "__main__":
    connect_to_db(app)
    # DebugToolbarExtension(app)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = False

    app.run(host="0.0.0.0", debug=True)
