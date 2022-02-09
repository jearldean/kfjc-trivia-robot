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

def make_a_count_question(question_str, table_dot_column, display_answer):
    column_quantity = common.get_count(table_dot_column, unique=True)
    acceptable_answers = {
        "calculate_answer": column_quantity,
        "answer_choice": f'{column_quantity:,}',
        "display_answer": display_answer}
    create_question(
        question=question_str,
        question_type="number",
        acceptable_answers=acceptable_answers)

def make_count_questions():
    parameterized_questions = [
        ["How many KFJC DJs are there?",
        Playlist.dj_id,
        "There are this many KFJC DJs!"],
        ["Since we started counting, how many shows have there been?",
        Playlist.id_,
        "There are this many shows in our records:"],
        ["Since we started counting, how many songs have been played on KFJC?",
        PlaylistTrack.id_,
        "We've played this many songs since we began keeping track!"],
        ["How many albums are in the KFJC Library?",
        Album.id_,
        "There are this many albums in our library:"],
        ["How many artists are in the KFJC Library?",
        Album.artist,
        "There are this many artists in our library:"],
        ["How many tracks are there in the KFJC Library?",
        Track.id_,
        "There are this many tracks in our library:"]
    ]
    for jj in parameterized_questions:
        make_a_count_question(
            question_str=jj[0],
            table_dot_column=jj[1],
            display_answer=jj[2])

def make_a_duration_question(question_str, duration_minutes, display_answer):
    acceptable_answers = {
        "calculate_answer": duration_minutes,
        "answer_choice": common.minutes_to_years(duration_minutes),
        "display_answer": display_answer}
    create_question(
        question=question_str,
        question_type="duration",
        acceptable_answers=acceptable_answers)

def make_duration_questions():
    parameterized_questions = [
        ["If a track is about 4 minutes long, how long would it take to listen to all tracks are in the KFJC Library?",
        4 * common.get_count(Track.id_, unique=True),
        "It would take this long to listen to all the tracks in the KFJC Library!"
        ]]
    for jj in parameterized_questions:
        make_a_duration_question(
            question_str=jj[0],
            duration_minutes=jj[1],
            display_answer = jj[2])

def make_a_date_question(question_str, isoformat_date_time_str, display_answer):
    print(isoformat_date_time_str, type(isoformat_date_time_str))
    
    acceptable_answers = {
        "calculate_answer": isoformat_date_time_str,
        "answer_choice": common.make_date_pretty(isoformat_date_time_str),
        "display_answer": display_answer}
    create_question(
        question=question_str,
        question_type="date",
        acceptable_answers=acceptable_answers)

def make_date_questions():
    oldest_playlist, newest_playlist = common.get_age(Playlist.start_time)
    parameterized_questions = [
        ["When did KFJC begin collecting this data?",
        oldest_playlist,
        "We began collecting this data on:"],
        ["Just how fresh is this data?",
        newest_playlist, 
        "The last data scrape for this page was on:"]
    ]
    for jj in parameterized_questions:
        make_a_date_question(
            question_str=jj[0],
            isoformat_date_time_str=jj[1],
            display_answer=jj[2])

def seed_all_question_types():
    make_count_questions()
    make_duration_questions()
    make_date_questions()
    db.session.commit()


def make_dj_date_questions(n=10):
    for _ in range(n):
        rando_dj_id = playlists.get_random_dj_id()
        _, date_time_first_show, _ = playlists.a_dj_is_born(dj_id=rando_dj_id)
        air_name, date_time_last_show, _ = playlists.last_show_by_dj_id(dj_id=rando_dj_id)
        create_question(
            question=f"When was {air_name}'s first show?",
            question_type="date",
            acceptable_answers=[date_time_first_show])
        create_question(
            question=f"When was {air_name}'s last show?",
            question_type="date",
            acceptable_answers=[date_time_last_show])
    db.session.commit() 

def get_random_question():
    """Get a random question."""
    # We're going to be deleting question rows dring development...
    # Keeping a pristine index for such a small table seems less efficient.
    random_question_id = choice(db.session.query(Question.question_id).distinct())
    return Question.query.get(random_question_id)

def get_unique_question(user_id):
    """Make sure the user has never been asked this question before."""
    users_answers = Answer.query.filter(Answer.user_id == user_id).all()
    user_already_answered = [users_answer.question_id for users_answer in users_answers]
    question_ids = [one_question.question_id for one_question in get_questions()]
    allowed_pool = list(set(question_ids) - set(user_already_answered))
    if allowed_pool:
        random_question_id = choice(allowed_pool)
        return Question.query.get(random_question_id)
    else:
        return "You've answered EVERY question! How about listening to some music?"


def get_answer_pile(question_instance):
    answer_pile = get_three_wrong_answers(question_instance)
    answer_pile.append(get_one_right_answer(question_instance))
    shuffle(answer_pile)
    return answer_pile

def get_one_right_answer(question_instance):
    """Get an acceptable_answer for multiple choice question."""
    if question_instance.question_type in ["number", "date", "duration"]:
        # There is only one choice for these types:
        return question_instance.acceptable_answers["answer_choice"]
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
