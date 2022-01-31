"""Question operations for KFJC Trivia Robot."""

from model import db, connect_to_db, UserAnswer, Question
from random import choice, choices

import common
import playlists
import playlist_tracks
import albums
import tracks
import collection_tracks


def create_question(question, acceptable_answers):
    """Create and return a new question."""

    question = Question(question=question,
                        acceptable_answers=acceptable_answers)

    db.session.add(question)
    # Don't forget to call model.db.session.commit() when done adding items.

    return question


def get_questions():
    """Get all questions."""

    return Question.query.all()

def get_question_by_id(question_id):
    """Return one question."""

    return Question.query.get(question_id)


def get_random_question():
    """Get a random question."""

    # TODO: Eliminate User's Already-Answered Questions from the reply

    num_questions = Question.query.count()
    random_pk = choice(range(1, num_questions+1))
    return Question.query.get(random_pk)


def get_unique_question(user_id):
    """Make sure the user has never been asked this question before."""

    return Question.query.filter(Question.question_id.not_in(
        UserAnswer.query.filter(UserAnswer.user_id == user_id).all()))


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

def add_qs_tracks_with_rando_word_in_title():
    pass
    #db.session.commit()

def get_all_tracks_with_word_in_title(word):
    a = collection_tracks.get_collection_tracks_with_word_in_title(word)
    b = tracks.get_tracks_with_word_in_title(word)
    return a + b

def add_q_random_album_by_a_djs_top_artist():
    # TODO: getting the top_n list is what takes a lot of time.
    # For each time we do that, seed about 3-5 questions from top_n.
    air_name, rando_artist, album_title, acceptable_answers = random_album_by_a_djs_top_artist()
    #dj_moniker = ["DJ", "KFJC DJ", "Dee-J"]
    verbs = ["likes to play", "plays a lot of", "seems to play a lot of", 
        "sure likes to play", "often plays"]
    rando_verb = choice(verbs)
    create_question(
        question=f"KFJC DJ {air_name} {rando_verb} the artist {rando_artist}. Can you name a track from their album {album_title}?",
        acceptable_answers=acceptable_answers)
    db.session.commit()

def random_album_by_a_djs_top_artist():
    air_name, top_artists = random_djs_top_artists()
    rando_artist = choice(top_artists)
    all_albums_by_artist = albums.get_albums_by_artist(artist=rando_artist)
    rando_album = choice(all_albums_by_artist)
    acceptable_answers = albums.lookup_track_names(album_instance=rando_album)
    return air_name, rando_artist, rando_album.title, acceptable_answers
    
def random_djs_top_artists():
    user_id, air_name = get_random_dj()
    top_artists = user_ids_top_n_artists(user_id=user_id, n=10)
    return air_name, top_artists

def user_ids_top_n_artists(user_id, n=10):
    playlist_track_artists = popular_artist_by_user_id(user_id=user_id)
    top_artists = common.top_n(
        popularity_dict=playlist_track_artists, n=n)
    return top_artists

def print_sir_c_most_popular_artists():
    playlist_track_artists = popular_artist_by_user_id(user_id=255)
    common.print_a_popularity_dict_in_order(
        popularity_dict=playlist_track_artists, min_items_required=10)
    return playlist_track_artists

def popular_artist_by_user_id(user_id):
    playlist_track_artists = {}
    user_ids_playlists = playlists.get_playlists_by_user_id(user_id=user_id)
    for user_ids_playlist in user_ids_playlists:
        playlist_track_rows = playlist_tracks.get_playlist_tracks_by_user_id(playlist_id=user_ids_playlist.playlist_id)
        for playlist_track_row in playlist_track_rows:
            playlist_track_artist = playlist_track_row.artist
            if playlist_track_artist not in ['NULL', ""]:
                playlist_track_artists[playlist_track_artist] = (
                    playlist_track_artists.get(playlist_track_artist, 0) + 1)
    return playlist_track_artists

def get_random_dj():
    user_id, air_name = playlists.get_random_air_name()
    return user_id, air_name

def wrong_answer_generator(data_type, acceptable_answers, k=3):
    """For multiple choice questions: Select items of the same
    data_type (tracks, artists, albums, air_names) 
    not in acceptable_answers."""
    if data_type == 'tracks':
        pass
    elif data_type == 'artists':
        pass
    elif data_type == 'albums':
        pass
    elif data_type == 'air_names':
        pass
    
    

if __name__ == '__main__':
    """Will connect you to the database when you run questions.py interactively"""
    from server import app
    connect_to_db(app)
