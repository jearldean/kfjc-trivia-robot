"""Server for KFJC Trivia Robot app."""

import os
from random import choice
from typing import List, Dict, Any, Tuple, Union
from jinja2 import StrictUndefined
from operator import itemgetter
from flask import (Flask, render_template, request, flash, session, redirect)
from flask_restful import Api, Resource  # reqparse
from flask_marshmallow import Marshmallow
from flask_restful_swagger import swagger
from werkzeug.wrappers import Response

from model import (
    db, connect_to_db, Answer, Playlist, PlaylistTrack, Album, Track)
import djs
import playlists
import playlist_tracks
import tracks
import albums
import users
import questions
import answers
import common

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
app.jinja_env.undefined = StrictUndefined
# api = Api(app)
api = swagger.docs(Api(app), apiVersion='0.1')
ma = Marshmallow(app)

TOP_N_USERS = 40  # Displayed on Leaderboard
ROBOT_MSG = [
    "Robot loves you!", "Pretty good, meatbag!",
    "Well done, bag of mostly water!", "Pretty good for a human!",
    "Robot is proud of you!"]
dj_dict = {}
dj_airnames = []

# -=-=-=-=-=-=-=-=-=-=-=- Routes -=-=-=-=-=-=-=-=-=-=-=-


@app.route("/")
def homepage() -> Response:
    """Display homepage."""

    if not dj_dict or not dj_airnames:
        retrieve_dj_stats_only_once()

    return render_template(
        'homepage.html',
        random_robot_img=random_robot_image(),
        greeting=assemble_greeting(),
        footer='public')


@app.route("/play")
def shall_we_play() -> Response:
    """Proceed with game or not."""

    game_on = request.args.get("game-on")  # Bool

    if game_on == 'true':
        return redirect('/question')
    else:
        # Send user to KFJC.org "Listen Now".
        return redirect('https://kfjc.org/player')


@app.route('/login', methods=['POST'])
def login_process() -> Response:
    """Process login."""
    username = request.form["username"]
    password_from_form = request.form["password"]

    user_instance = users.get_user_by_username(username=username)

    if not user_instance:
        flash("No one with that username found.")
        return redirect("/")
    if users.does_password_match(
            user_instance=user_instance,
            password_from_form=password_from_form):
        session["user_id"] = user_instance.user_id
        return redirect("/question")
    else:
        flash("Oops, password didn't match.")
        return redirect("/")


@app.route('/create_account', methods=['POST'])
def create_account() -> Response:
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
def important() -> Response:
    """Important info for logged in users."""

    flash("Make an account to take a fun quiz.")
    return redirect("/")


@app.route("/logout")
def logout() -> Response:
    """User must be logged in."""
    if "user_id" not in session:
        return redirect('/important')
    del session["user_id"]
    if "question_id" in session:
        del session["question_id"]
    flash("Logged Out.")
    return redirect("/")


@app.route("/infopage")
def infopage() -> Response:

    if "user_id" not in session:
        footer = 'public'
    else:
        footer = 'private'

    return render_template(
        'infopage.html',
        random_robot_img=random_robot_image(),
        footer=footer)


@app.route("/score")
def myscore() -> Response:
    if "user_id" not in session:
        return redirect('/important')

    user_id = session["user_id"]
    user = users.get_user_by_id(user_id=user_id)
    user_score_named_tuple = answers.get_user_score(user_id=user_id)

    return render_template(
        'score.html',
        robot_msg=choice(ROBOT_MSG),
        random_robot_img=random_robot_image(),
        fname=user.fname,
        user_score=user_score_named_tuple,
        footer='private')


@app.route("/question")
def ask_question() -> Response:
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
            question_type=next_question.question_type,
            ask_question=next_question.ask_question,
            display_shuffled_answers=next_question.display_shuffled_answers,
            footer='private')


@app.route("/answer", methods=["POST"])
def answer_question() -> Response:
    """Grade user response and display correct answer."""

    answer_given = request.form.get("q")
    user = users.get_user_by_id(user_id=session["user_id"])
    question = questions.get_question_by_id(question_id=session["question_id"])

    answer = answers.create_answer(
        user_instance=user,
        question_instance=question,
        answer_given=answer_given)
    db.session.commit()

    if answer_given == "SKIP":  # That's a skip.
        return redirect('/question')

    user_msg = answers.get_user_msg(answer=answer)

    if answer.answer_correct:
        happy_or_sad_robot = random_robot_image(happy=True)
    else:
        happy_or_sad_robot = random_robot_image(happy=False)

    return render_template(
        'answer.html',
        random_robot_img=happy_or_sad_robot,
        user_msg=user_msg,
        answer_correct=answer.answer_correct,
        present_answer=question.present_answer,
        the_right_answer=question.acceptable_answer,
        present_answer_data_headings=question.present_answer_data_headings,
        present_answer_data=question.present_answer_data,
        footer='private')


@app.route("/ask")
def user_asks() -> Response:
    """user can ask the robot a question!"""
    if not dj_dict or not dj_airnames:
        retrieve_dj_stats_only_once()

    if "user_id" not in session:
        return redirect('/important')

    dj_id = request.args.get("dj_id")
    if not dj_id:
        print(dj_airnames[0])
        selected_dj_id = choice(dj_airnames)[0]
    else:
        selected_dj_id = int(dj_id)  # Only strings come back from forms.
    session['selected_dj_id'] = selected_dj_id
    dj_stat = dj_dict[selected_dj_id]['dj_stats']

    return render_template(
        'ask.html',
        random_robot_img=random_robot_image(),
        dj_airnames=dj_airnames,
        dj_dict=dj_dict,
        dj_most_plays_headings=False,
        selected_dj_id=session['selected_dj_id'],
        dj_stat=dj_stat,
        footer='private')


@app.route("/leaderboard")
def leaderboard() -> Response:
    """Show top scores."""

    if "user_id" not in session:
        return redirect('/important')

    score_board = answers.compile_leaderboard()

    table_range = min(TOP_N_USERS, len(score_board))
    if session["user_id"] in [f[0] for f in score_board[:table_range]]:
        user_msg = f"You're in the KFJC Top{TOP_N_USERS}!"
    else:
        user_msg = f"Our Top{TOP_N_USERS} Leaders:"

    return render_template(
        'leaderboard.html',
        random_robot_img=random_robot_image(),
        robot_msg=choice(ROBOT_MSG),
        table_range=table_range,
        current_user=session["user_id"],
        user_msg=user_msg,
        leaders=score_board,
        footer='private')

# -=-=-=-=-=-=-=-=-=-=-=- Python -=-=-=-=-=-=-=-=-=-=-=-


def random_robot_image(happy: Union[bool, None] = None) -> str:
    """Give a path to a robot image."""

    if happy is None:
        robot_picture_idx = choice(range(1, 13))
    elif happy is False:
        robot_picture_idx = choice([7, 8, 11, 12])
    else:  # happy is True
        robot_picture_idx = choice([4, 6, 9])

    return f"static/img/robot{robot_picture_idx}.png"


def assemble_greeting() -> str:
    """Gather stats for to make a compelling reason to take a database quiz."""

    first_and_last_show = playlists.first_show_last_show()
    first_show_in_db = common.make_date_pretty(first_and_last_show[0])
    duration = common.minutes_to_years(
        ((first_and_last_show[1] - first_and_last_show[0]).total_seconds())/60)
    count_all_shows = common.format_an_int_with_commas(
        playlists.how_many_shows())
    count_prolific_djs = common.format_an_int_with_commas(
        playlists.how_many_djs())
    count_playlist_tracks = common.format_an_int_with_commas(
        playlist_tracks.how_many_tracks())

    greeting = (
        f"KFJC has a database going back to {first_show_in_db} "
        f"that contains {count_all_shows} shows by {count_prolific_djs} DJs. "
        f"They've played {count_playlist_tracks} songs in {duration}! "
        f"Wanna play a trivia game with me?")
    return greeting


def retrieve_dj_stats_only_once() -> Tuple:
    djs_alphabetically = playlists.get_djs_alphabetically()
    for zz in djs_alphabetically:
        dj_id = zz.dj_id
        air_name = djs.get_airname_for_dj(dj_id=dj_id)
        air_name_posessive = djs.get_airname_for_dj(
            dj_id=dj_id, posessive=True)
        showcount = common.format_an_int_with_commas(zz.showcount)
        firstshow = common.make_date_pretty(zz.firstshow)
        lastshow = common.make_date_pretty(zz.lastshow)
        dj_stats = (
            f"{air_name_posessive} first show was on {firstshow}, "
            f"their last show was on {lastshow} and they have done "
            f"{showcount} shows!")
        dj_dict[dj_id] = {
            'air_name': air_name,
            'showcount': showcount,
            'firstshow': firstshow,
            'lastshow': lastshow,
            'dj_stats': dj_stats}
        dj_airnames.append([dj_id, air_name])
    return dj_dict, dj_airnames

# -=-=-=-=-=-=-=-=-=-=-=- REST API: Leaderboard -=-=-=-=-=-=-=-=-=-=-=-
# http://0.0.0.0:5000/rest_leaderboard


class LeaderboardSchema(ma.Schema):
    class Meta:
        fields = (
            "username", "fname", "passed",
            "failed", "skipped", "questions", "percent")


leaderboard_schema = LeaderboardSchema(many=True)


@swagger.model
class LeaderboardResource(Resource):
    "Leaderboard"
    @swagger.operation(
        notes='User Scores in order of Percent Correct',
        responseClass=Answer.__name__,
        nickname='leader',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": Answer.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self) -> List[Dict[str, Any]]:
        score_board = []
        for user in users.get_users():
            user_score = {}
            user_score_named_tuple = answers.get_user_score(
                user_id=user.user_id)
            user_score["username"] = user.username
            user_score["fname"] = user.fname
            user_score["passed"] = user_score_named_tuple.passed
            user_score["failed"] = user_score_named_tuple.failed
            user_score["skipped"] = user_score_named_tuple.skipped
            user_score["questions"] = user_score_named_tuple.questions
            user_score["percent"] = user_score_named_tuple.percent
            score_board.append(user_score)

        score_board.sort(key=itemgetter("percent"), reverse=True)
        return leaderboard_schema.dump(score_board)

# Don't make a confilct with @app.route("/leaderboard")


api.add_resource(LeaderboardResource, '/rest_leaderboard')

# -=-=-=-=-=-=-=-=-=-=-=- REST API: Playlists -=-=-=-=-=-=-=-=-=-=-=-
# http://0.0.0.0:5000/playlists/66582
# http://0.0.0.0:5000/playlists/66581


class PlaylistSchema(ma.Schema):
    class Meta:
        fields = (
            "id_", "kfjc_playlist_id", "dj_id",
            "air_name", "start_time", "end_time")


playlist_schema = PlaylistSchema()
playlists_schema = PlaylistSchema(many=True)


@swagger.model
class PlaylistResource(Resource):
    "Playlist"
    @swagger.operation(
        notes='One show by a DJ',
        responseClass=Playlist.__name__,
        nickname='playlist',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": Playlist.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, kfjc_playlist_id: int) -> List[Dict[str, Any]]:
        playlist = Playlist.query.get_or_404(kfjc_playlist_id)
        return playlist_schema.dump(playlist)


api.add_resource(PlaylistResource, '/playlists/<int:kfjc_playlist_id>')

# -=-=-=-=-=-=-=-=-=-=-=- REST API: Playlist Tracks -=-=-=-=-=-=-=-=-=-=-=-
# http://0.0.0.0:5000/playlist_tracks/66582
# http://0.0.0.0:5000/playlist_tracks/66581


class PlaylistTracksSchema(ma.Schema):
    class Meta:
        fields = (
            "kfjc_playlist_id", "indx", "kfjc_album_id",
            "album_title", "artist", "track_title", "time_played")


playlist_tracks_schema = PlaylistTracksSchema(many=True)


@swagger.model
class PlaylistTracksResource(Resource):
    "PlaylistTracks"
    @swagger.operation(
        notes="Tracks played during one show",
        responseClass=PlaylistTrack.__name__,
        nickname='playlist_tracks',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": PlaylistTrack.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, kfjc_playlist_id: int) -> List[Dict[str, Any]]:
        playlist_tracks_found = (
            playlist_tracks.get_playlist_tracks_by_kfjc_playlist_id(
                kfjc_playlist_id=kfjc_playlist_id))
        return playlist_tracks_schema.dump(playlist_tracks_found)


api.add_resource(
    PlaylistTracksResource, '/playlist_tracks/<int:kfjc_playlist_id>')

# -=-=-=-=-=-=-=-=-=-=-=- REST API: DJ Favorites -=-=-=-=-=-=-=-=-=-=-=-
# http://0.0.0.0:5000/dj_favorites/album/dj_id=255
# http://0.0.0.0:5000/dj_favorites/artist/dj_id=255
# http://0.0.0.0:5000/dj_favorites/track/dj_id=255


class DJFavoritesSchema(ma.Schema):
    class Meta:
        fields = ("dj_id", "artist", "album_title", "track_title", "plays")


one_dj_favorites_schema = DJFavoritesSchema(many=True)


@swagger.model
class DJFavoriteArtistResource(Resource):
    "DJs Favorite Artists"
    @swagger.operation(
        notes="Top plays of artists by one DJ",
        responseClass=PlaylistTrack.__name__,
        nickname='dj_favorite_artist',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": PlaylistTrack.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, dj_id: int) -> List[Dict[str, Any]]:
        favorites = playlist_tracks.get_favorite_artists(
            dj_id=dj_id, reverse=True, min_plays=5)
        if not favorites:
            warning_string = playlist_tracks.dj_needs_more_shows(dj_id)
            masquerade_as_data = [{'artist': "", "plays": warning_string}]
            favorites = common.convert_list_o_dicts_to_list_o_named_tuples(
                masquerade_as_data)
        return one_dj_favorites_schema.dump(favorites)


@swagger.model
class DJFavoriteAlbumResource(Resource):
    "DJs Favorite Albums"
    @swagger.operation(
        notes="Top plays of albums by one DJ",
        responseClass=PlaylistTrack.__name__,
        nickname='dj_favorite_album',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": PlaylistTrack.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, dj_id: int) -> List[Dict[str, Any]]:
        favorites = playlist_tracks.get_favorite_albums(
            dj_id=dj_id, reverse=True, min_plays=5)
        if not favorites:
            warning_string = playlist_tracks.dj_needs_more_shows(dj_id)
            masquerade_as_data = [{'album_title': "", "plays": warning_string}]
            favorites = common.convert_list_o_dicts_to_list_o_named_tuples(
                masquerade_as_data)
        return one_dj_favorites_schema.dump(favorites)


@swagger.model
class DJFavoriteTrackResource(Resource):
    "DJs Favorite Tracks"
    @swagger.operation(
        notes="Top plays of tracks by one DJ",
        responseClass=PlaylistTrack.__name__,
        nickname='dj_favorite_track',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": PlaylistTrack.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, dj_id: int) -> List[Dict[str, Any]]:
        favorites = playlist_tracks.get_favorite_tracks(
            dj_id=dj_id, reverse=True, min_plays=5)
        if not favorites:
            warning_string = playlist_tracks.dj_needs_more_shows(dj_id)
            masquerade_as_data = [{'track_title': "", "plays": warning_string}]
            favorites = common.convert_list_o_dicts_to_list_o_named_tuples(
                masquerade_as_data)
        return one_dj_favorites_schema.dump(favorites)


api.add_resource(
    DJFavoriteArtistResource, '/dj_favorites/artist/dj_id=<int:dj_id>')
api.add_resource(
    DJFavoriteAlbumResource, '/dj_favorites/album/dj_id=<int:dj_id>')
api.add_resource(
    DJFavoriteTrackResource, '/dj_favorites/track/dj_id=<int:dj_id>')

# -=-=-=-=-=-=-=-=-=-=-=- REST API: Last Played -=-=-=-=-=-=-=-=-=-=-=-
# http://0.0.0.0:5000/last_played/artist=Pink%20Floyd
# http://0.0.0.0:5000/last_played/album=Dark%20Side%20of%20the%20Moon
# http://0.0.0.0:5000/last_played/track=eclipse


class LastPlayedSchema(ma.Schema):
    class Meta:
        fields = (
            "air_name", "artist", "album_title",
            "track_title", "time_played")


last_played_schema = LastPlayedSchema(many=True)


@swagger.model
class LastPlayedByArtist(Resource):
    "Last Plays of Artist"
    @swagger.operation(
        notes="Last plays of artists containing the search_word",
        responseClass=PlaylistTrack.__name__,
        nickname='last_played_artist',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": PlaylistTrack.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, artist: str) -> List[Dict[str, Any]]:
        last_time_played = playlist_tracks.get_last_play_of_artist(
            artist=artist, reverse=True)
        return last_played_schema.dump(last_time_played)


@swagger.model
class LastPlayedByAlbum(Resource):
    "Last Plays of Album"
    @swagger.operation(
        notes="Last plays of albums containing the search_word",
        responseClass=PlaylistTrack.__name__,
        nickname='last_played_album',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": PlaylistTrack.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, album: str) -> List[Dict[str, Any]]:
        last_time_played = playlist_tracks.get_last_play_of_album(
            album=album, reverse=True)
        return last_played_schema.dump(last_time_played)


@swagger.model
class LastPlayedByTrack(Resource):
    "Last Plays of Tracks"
    @swagger.operation(
        notes="Last plays of tracks containing the search_word",
        responseClass=PlaylistTrack.__name__,
        nickname='last_played_track',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": PlaylistTrack.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, track: str) -> List[Dict[str, Any]]:
        last_time_played = playlist_tracks.get_last_play_of_track(
            track=track, reverse=True)
        return last_played_schema.dump(last_time_played)


api.add_resource(LastPlayedByArtist, '/last_played/artist=<string:artist>')
api.add_resource(LastPlayedByAlbum, '/last_played/album=<string:album>')
api.add_resource(LastPlayedByTrack, '/last_played/track=<string:track>')

# -=-=-=-=-=-=-=-=-=-=-=- REST API: Top Ten -=-=-=-=-=-=-=-=-=-=-=-
# http://0.0.0.0:5000/top_plays/top=5&order_by=artist&start_date=2020-01-02&end_date=2020-01-10
# http://0.0.0.0:5000/top_plays/top=5&order_by=artists&start_date=2021-01-02&end_date=2021-01-10
# http://0.0.0.0:5000/top_plays/top=5&order_by=album&start_date=2022-01-02&end_date=2022-01-10
# http://0.0.0.0:5000/top_plays/top=5&order_by=albums&start_date=2020-01-02&end_date=2020-01-10
# http://0.0.0.0:5000/top_plays/top=5&order_by=track&start_date=2020-01-02&end_date=2020-01-10


class TopTenSchema(ma.Schema):
    class Meta:
        fields = ("plays", "artist", "album_title", "track_title")


top_n_artist_schema = TopTenSchema(many=True)


@swagger.model
class TopTen(Resource):
    "Top Plays"
    @swagger.operation(
        notes="Top plays between two dates",
        responseClass=PlaylistTrack.__name__,
        nickname='top plays',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": PlaylistTrack.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(
            self, order_by: str, start_date: str, end_date: str, top: int = 10
            ) -> List[Dict[str, Any]]:
        if order_by in ['artist', 'artists']:
            top_10 = playlist_tracks.get_top10_artists(
                start_date, end_date, n=top)
        if order_by in ['album', 'albums']:
            top_10 = playlist_tracks.get_top10_albums(
                start_date, end_date, n=top)
        else:    # order_by in ['track', 'tracks']:
            top_10 = playlist_tracks.get_top10_tracks(
                start_date, end_date, n=top)

        return top_n_artist_schema.dump(top_10)


api.add_resource(
    TopTen,
    '/top_plays/top=<int:top>&order_by=<string:order_by>'
    '&start_date=<string:start_date>&end_date=<string:end_date>')

# -=-=-=-=-=-=-=-=-=-=-=- REST API: DJ Stats -=-=-=-=-=-=-=-=-=-=-=-
# http://0.0.0.0:5000/dj_stats

# http://0.0.0.0:5000/dj_stats/order_by=air_name&reverse=1
# http://0.0.0.0:5000/dj_stats/order_by=air_name&reverse=0
# http://0.0.0.0:5000/dj_stats/order_by=dj_id&reverse=1
# http://0.0.0.0:5000/dj_stats/order_by=showcount&reverse=1
# http://0.0.0.0:5000/dj_stats/order_by=firstshow&reverse=0
# http://0.0.0.0:5000/dj_stats/order_by=lastshow&reverse=1


class DJStatsSchema(ma.Schema):
    class Meta:
        fields = ("air_name", "dj_id", "showcount", "firstshow", "lastshow")


dj_stats_schema = DJStatsSchema(many=True)


@swagger.model
class DJStatsNoArgs(Resource):
    "DJs by air_name"
    @swagger.operation(
        notes="DJs on order of air_name",
        responseClass=Playlist.__name__,
        nickname='DJ air_names',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": Playlist.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self) -> List[Dict[str, Any]]:
        dj_stats = playlists.get_djs_alphabetically()
        return dj_stats_schema.jsonify(dj_stats)


@swagger.model
class DJStats(Resource):
    "DJs by various accomplishments"
    @swagger.operation(
        notes="DJs by first_show, last_show, show_count, dj_id or air_name",
        responseClass=Playlist.__name__,
        nickname='DJ Stats',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": Playlist.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(
            self, order_by: str = 'air_name', reverse: int = 1
            ) -> List[Dict[str, Any]]:
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
        return dj_stats_schema.jsonify(dj_stats)


api.add_resource(
    DJStats,
    '/dj_stats/order_by=<string:order_by>&reverse=<int:reverse>')
api.add_resource(DJStatsNoArgs, '/dj_stats')

# -=-=-=-=-=-=-=-=-=-=-=- REST API: Album Tracks -=-=-=-=-=-=-=-=-=-=-=-
# http://0.0.0.0:5000/album_tracks/303
# http://0.0.0.0:5000/album_tracks/15141
# http://0.0.0.0:5000/album_tracks/497606


class AlbumTracksSchema(ma.Schema):
    class Meta:
        fields = ("indx", "title", "artist")


album_tracks_schema = AlbumTracksSchema(many=True)


@swagger.model
class AlbumTracks(Resource):
    "Tracks on an Album"
    @swagger.operation(
        notes="Tracks on an Album",
        responseClass=Track.__name__,
        nickname='Album Tracks',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": Track.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, kfjc_album_id: int) -> List[Dict[str, Any]]:
        album_tracks = tracks.get_tracks_by_kfjc_album_id(kfjc_album_id)
        return album_tracks_schema.dump(album_tracks)


api.add_resource(AlbumTracks, '/album_tracks/<int:kfjc_album_id>')

# -=-=-=-=-=-=-=-=-=-=-=- Albums by an Artist -=-=-=-=-=-=-=-=-=-=-=-
# http://0.0.0.0:5000/artists_albums/artist=Pink%20Floyd
# http://0.0.0.0:5000/artists_albums/artist=Lee%20Press%20On
# http://0.0.0.0:5000/artists_albums/artist=Adam%20Ant

"""choice here: collections (multiple artists on an album) will be skipped if
we use the albums table lookup. But if we back it out from the tracks table,
compilation albums would be included."""


class ArtistsAlbumsSchema(ma.Schema):
    class Meta:
        fields = ("kfjc_album_id", "album_title", "artist")


artists_albums_schema = ArtistsAlbumsSchema(many=True)


@swagger.model
class ArtistsAlbums(Resource):
    "Albums by an Artist"
    @swagger.operation(
        notes="Albums by an Artist",
        responseClass=Album.__name__,
        nickname='Artist\'s Albums',
        parameters=[
            {
              "name": "body",
              "description": "blueprint object that needs to be added. YAML.",
              "required": True,
              "allowMultiple": False,
              "dataType": Album.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. created blueprint URL in Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, artist: str) -> List[Dict[str, Any]]:
        albums_by_artist = []
        tracks_by_artist = tracks.get_tracks_by_an_artist(artist=artist)
        for track_by_artist in tracks_by_artist:
            kfjc_album_id = track_by_artist.kfjc_album_id
            album = albums.get_album_by_id(kfjc_album_id=kfjc_album_id)
            report_artist = track_by_artist.artist
            to_be_appended = {
                    "kfjc_album_id": kfjc_album_id, "album_title": album.title,
                    "artist": report_artist}
            if to_be_appended not in albums_by_artist:
                albums_by_artist.append(to_be_appended)
        return artists_albums_schema.dump(albums_by_artist)


api.add_resource(ArtistsAlbums, '/artists_albums/artist=<string:artist>')

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

if __name__ == "__main__":
    connect_to_db(app)
    # DebugToolbarExtension(app)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = False

    app.run(host="0.0.0.0", debug=False)
