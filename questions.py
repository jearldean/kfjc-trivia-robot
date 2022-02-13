"""Question operations for KFJC Trivia Robot."""

from random import choice, randrange, shuffle  # choices, randint, 

from model import db, connect_to_db, Question, Answer, Playlist, PlaylistTrack, Album, Track
import common
import playlists


def create_question(question, question_type, acceptable_answers):
    """Create and return a new question."""

    question = Question(
        question=question,
        question_type=question_type,
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


def get_unique_question(user_id):
    """Make sure the user has never been asked this question before."""
 
    users_answers = Answer.query.filter(Answer.user_id == user_id).all()
    user_already_answered = [users_answer.question_id for users_answer in users_answers]
    question_ids = [one_question.question_id for one_question in get_questions()]
    allowed_pool = list(set(question_ids) - set(user_already_answered))
    if allowed_pool:
        random_question_id = choice(allowed_pool)
        return get_question_by_id(question_id=random_question_id)
        # TODO use try/except instead of returning 2 different data types.
    else:
        return "You've answered EVERY question! How about listening to some music?"


def get_answer_pile(question_instance):
    if question_instance.question_type in ["most_shows", "earliest_show"]:
        answer_pile = question_instance.acceptable_answers["display_incorrect_answers"]
        answer_pile.append(question_instance.acceptable_answers["display_answer"])
    else:
        answer_pile = get_three_wrong_answers(question_instance)
        answer_pile.append(get_one_right_answer(question_instance))
    shuffle(answer_pile)
    return answer_pile

def get_one_right_answer(question_instance):
    """Get an acceptable_answer for multiple choice question."""
    if question_instance.question_type in ["number", "date", "duration"]:
        # There is only one choice for these types:
        return question_instance.acceptable_answers["display_answer"]
    else:
        return ""

def get_three_wrong_answers(question_instance, k=3, percent=40):
    """Get three unacceptable yet mildly convincing answers for
    multiple choice questions."""
    if question_instance.question_type == "number":
        raw_numbers = common.random_number_within_percent(
            target_number=question_instance.acceptable_answers["calculate_answer"],
            percent=40, k=4)
        some_randos = []
        for ii in raw_numbers:
            some_randos.append(f'{ii:,}')
    elif question_instance.question_type == "date":
        some_randos = common.random_date_surrounding_another_date(
            target_date_time=question_instance.acceptable_answers["calculate_answer"], k=4)
    elif question_instance.question_type == "duration":
        # Cheap way of doing it for now:
        some_randos = []
        for _ in range(4):
            years = randrange(3, 15)
            weeks = randrange(0, 52)
            days = randrange(1, 8)
            day_fraction = randrange(0, 10)
            some_randos.append(f"{years} years, {weeks} weeks, and {days}.{day_fraction} days")
    else:
        print(f"No handler for question_type={question_instance.question_type}")
        return []
    # Selecting 3 from a pack of 4 values will allow the 
    # answer number to sometimes appear as the max or min of values presented:
    return some_randos[:3]


"""
def four_djs_walk_into_a_bar():
    dj_ids_list = playlists.get_4_random_dj_ids()
    display_names = []
    ages = []
    num_playlists = []
    for dj_id in dj_ids_list:
        air_name, birthday, statement = playlists.a_dj_is_born(dj_id=dj_id)
        air_name, count_playlists, their_playlists = playlists.get_all_playlists_by_dj_id(dj_id=dj_id)
        display_names.append(air_name)
        ages.append(birthday)
        num_playlists.append(count_playlists)
    create_question(
        question="Who has been on the air the longest?",
        question_type="date",
        acceptable_answers=[min(birthday)])
    create_question(
        question="Who has the most shows?",
        question_type="number",
        acceptable_answers=[max(count_playlists)])
    
def popular_artist_by_dj_id(dj_id):
    playlist_track_artists = {}
    djs_playlists = playlists.get_all_playlists_by_dj_id(dj_id=dj_id)
    for djs_playlist in djs_playlists:
        playlist_track_rows = playlist_tracks.get_playlist_tracks_by_user_id(playlist_id=user_ids_playlist.playlist_id)
        for playlist_track_row in playlist_track_rows:
            playlist_track_artist = playlist_track_row.artist
            if playlist_track_artist not in ['NULL', ""]:
                playlist_track_artists[playlist_track_artist] = (
                    playlist_track_artists.get(playlist_track_artist, 0) + 1)
    return playlist_track_artists

def add_qs_tracks_with_rando_word_in_title():
    pass
    #db.session.commit()

def seed_tracks_with_word_in_title():
    for word in ['moon', 'bird', 'dirty', 'blues', 'man', 'woman']:
        question = f"Can you name a song with '{word}' in the title?"
        acceptable_answer_objects = get_all_tracks_with_word_in_title(word)
        acceptable_answers = []
        for each_obj in acceptable_answer_objects:
            acceptable_answers.append(each_obj.title)
        create_question(
            question=question,
            acceptable_answers=acceptable_answers,
            acceptable_answer_objects=acceptable_answer_objects)

def get_all_tracks_with_word_in_title(word):
    a = collection_tracks.get_collection_tracks_with_word_in_title(word)
    b = tracks.get_tracks_with_word_in_title(word)
    return a + b

def seed_q_random_album_by_a_djs_top_artist(num_djs=5, num_artists=3):
    # call add_q_random_album_by_a_djs_top_artist() in an efficient manner:
    # for a few DJs and for a few of their fave artists.
    for dd in range(num_djs):
        user_id, air_name = get_random_dj()
        top_artists = user_ids_top_n_artists(user_id=user_id, n=num_artists)
        for rando_artist in top_artists:  #  Maybe it's fewer than num_artists for a new DJ?
            rando_verb = choice(["likes to play", "plays a lot of", "seems to play a lot of", 
                "sure likes to play", "often plays", "has played"])
            all_albums_by_artist = albums.get_albums_by_artist(artist=rando_artist)
            try:
                rando_album = choice(all_albums_by_artist)
            except IndexError:  # IndexError: list index out of range, I think there was no album found for the artist?
                continue
            acceptable_answer_objects = rando_album
            acceptable_answers = albums.lookup_track_names(rando_album)
            question=(
                f"KFJC DJ {air_name} {rando_verb} the artist {rando_artist}. Can you name a track from their album {rando_album.title}?")
            create_question(
                question=question,
                acceptable_answers=acceptable_answers,
                acceptable_answer_objects=acceptable_answer_objects)

def add_q_random_album_by_a_djs_top_artist():
    # TODO: getting the top_n list is what takes a lot of time.
    # For each time we do that, seed about 3-5 questions from top_n.
    air_name, rando_artist, album_title, acceptable_answers = random_album_by_a_djs_top_artist()
    #dj_moniker = ["DJ", "KFJC DJ", "Dee-J"]
    verbs = ["likes to play", "plays a lot of", "seems to play a lot of", 
        "sure likes to play", "often plays"]
    rando_verb = choice(verbs)
    create_question(
        question=f"KFJC DJ {air_name} {rando_verb} the artist {rando_artist}. Can you name a track from their album '{album_title}'?",
        acceptable_answers=acceptable_answers)

def random_album_by_a_djs_top_artist():
    air_name, top_artists = random_djs_top_artists()
    rando_artist = choice(top_artists)
    all_albums_by_artist = albums.get_albums_by_artist(artist=rando_artist)
    rando_album = choice(all_albums_by_artist)
    acceptable_answers = albums.lookup_track_names(album_instance=rando_album)
    return air_name, rando_artist, rando_album.title, acceptable_answers
    
def random_djs_top_artists(n=10):
    user_id, air_name = get_random_dj()
    top_artists = user_ids_top_n_artists(user_id=user_id, n=n)
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

"""

if __name__ == '__main__':
    """Will connect you to the database when you run questions.py interactively"""
    from server import app
    connect_to_db(app)
