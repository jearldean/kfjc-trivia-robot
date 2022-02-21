"""Question operations for KFJC Trivia Robot."""

from datetime import datetime, timedelta, date
from operator import itemgetter
from random import randrange, choice, choices, shuffle

from model import Answer, db, connect_to_db, Question, Album
import playlists
import playlist_tracks
import tracks
import common

SEED_QUESTION_COUNT = 30

def create_question(question_type, ask_question, present_answer, acceptable_answers, wrong_answers):
    """Create and return a new question."""

    question = Question(
        question_type=question_type,
        ask_question=ask_question,
        present_answer=present_answer,
        acceptable_answers=acceptable_answers,
        wrong_answers=wrong_answers)

    db.session.add(question)
    # Don't forget to call model.db.session.commit() when done adding items.

    return question

def get_question_by_id(question_id):
    return Question.query.get(question_id)
     
# -=-=-=-=-=-=-=-=-=-=-=- Seed Questions Table -=-=-=-=-=-=-=-=-=-=-=-

def make_all_the_questions():
    #who_is_the_oldest_dj()  # works
    #who_is_the_newest_dj()  # works
    #who_has_the_most_shows()  # works
    # which_is_djs_favorite_artist()  # works
    # which_is_djs_favorite_album()  # works
    # which_is_djs_favorite_track()  # works
    # top_ten_artist()
    # top_ten_album()
    # top_ten_track()
    # last_play_of_artist()
    # last_play_of_album()
    # last_play_of_track()
    # tracks_on_an_album()
    # when_was_dj_last_on_the_air()
    pass

def question_engine(
        resultproxy, answer_column, ask_questions, present_answers,
        search_key, reverse_display_answers):
    answer_key = common.unpack_a_result_proxy(resultproxy=resultproxy)
    winners = answer_key[:SEED_QUESTION_COUNT]  # list of dicts
    losers = answer_key[SEED_QUESTION_COUNT:]
    for the_right_answer in winners:
        three_wrong_answers = choices(losers, k=3)
        answer_pile = [the_right_answer] + three_wrong_answers
        present_answer_data = []
        display_shuffled_answers = []

        if search_key in ['firstshow', 'lastshow']:
            for zz in sorted(answer_pile, key=itemgetter(search_key), reverse=reverse_display_answers):
                item_value = common.make_date_pretty(date_time_string=zz[search_key])
                present_answer_data.append([zz[answer_column], item_value])
                display_shuffled_answers.append(zz[answer_column])
        elif search_key in ['showcount']:
            for zz in sorted(answer_pile, key=itemgetter(search_key), reverse=reverse_display_answers):
                item_value = common.format_an_int_with_commas(your_int=zz[search_key])
                present_answer_data.append([zz[answer_column], item_value])
                display_shuffled_answers.append(zz[answer_column])
        else:
            for zz in sorted(answer_pile, key=itemgetter(search_key), reverse=reverse_display_answers):
                item_value = item_value=zz[search_key]
                present_answer_data.append([zz[answer_column], item_value])
                display_shuffled_answers.append(zz[answer_column])

        acceptable_answers = [display_shuffled_answers[0]]
        shuffle(display_shuffled_answers)
        create_question(
            question_type=answer_column,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answers=acceptable_answers,
            wrong_answers=[display_shuffled_answers, present_answer_data])
    db.session.commit()

def who_is_the_oldest_dj():
    resultproxy = playlists.get_djs_by_first_show(reverse=False)
    answer_column = "air_name"
    ask_questions = [
        "Who was on the air first?", "Who was first on the air?",
        "Who was a DJ before any of the others?"]
    present_answers = [
        "This person was on the air first:", "This person hit the airwaves first:",
        "This DJ was first on the air:"]
    search_key = 'firstshow'
    reverse_display_answers = False
    question_engine(
        resultproxy=resultproxy, answer_column=answer_column,
        ask_questions=ask_questions, present_answers=present_answers,
        search_key=search_key, reverse_display_answers=reverse_display_answers)

def who_is_the_newest_dj():
    resultproxy = playlists.get_djs_by_first_show(reverse=True)
    answer_column = "air_name"
    ask_questions = [
        "Who is the newest DJ?", "Spot the greenhorn! Who is our newest DJ?",
        "Pick the rookie - who is the most recent DJ?"]
    present_answers = [
        "This person appeared on the air last:", "This person is newest to our airwaves:",
        "Here's the newest DJ from that lot:", "The newest DJ is:"]
    search_key = 'firstshow'
    reverse_display_answers = True
    question_engine(
        resultproxy=resultproxy, answer_column=answer_column,
        ask_questions=ask_questions, present_answers=present_answers,
        search_key=search_key, reverse_display_answers=reverse_display_answers)

def who_has_the_most_shows():
    resultproxy = playlists.get_djs_by_show_count()
    answer_column = "air_name"
    ask_questions = [
        "Who has the most shows?", "Who has done the most shows?",
        "Which DJ has the most shows?"]
    present_answers = [
        "This person has done the most shows:", "This person has the most shows:",
        "This DJ has more shows:"]
    search_key = 'showcount'
    reverse_display_answers = True
    question_engine(
        resultproxy=resultproxy, answer_column=answer_column,
        ask_questions=ask_questions, present_answers=present_answers,
        search_key=search_key, reverse_display_answers=reverse_display_answers)

def which_is_djs_favorite_artist():
    dj_id_pool = playlists.get_all_dj_ids()
    random_dj_ids = choices(dj_id_pool, k=SEED_QUESTION_COUNT)
    for dj_id in random_dj_ids:
        resultproxy = playlist_tracks.get_favorite_artists(dj_id=dj_id, reverse=True, min_plays=5)
        answer_key = common.unpack_a_result_proxy(resultproxy=resultproxy)
        try:
            air_name = playlists.get_airname(dj_id)
        except AttributeError:
            continue  # Dudd DJ.
        if len(answer_key) < 20:
            continue  # Dudd DJ.
        answer_column = "artist"
        winners = answer_key[:10]
        losers = answer_key[10:]
        for the_right_answer in winners:
            ask_questions = [
                f"Who does {air_name} like most?", f"Which artist is {air_name}'s favorite?",
                f"Who has {air_name} played the most?"]
            present_answers = [
                f"{air_name} likes this artist the most:", f"{air_name} has played this artist the most:",
                f"This artist is played by {air_name} a lot:"]
            three_wrong_answers = choices(losers, k=3)
            answer_pile = [the_right_answer] + three_wrong_answers
            present_answer_data = []
            display_shuffled_answers = []
            for zz in sorted(answer_pile, key=itemgetter('plays'), reverse=True):
                present_answer_data.append([zz['artist'], zz['plays']])
                display_shuffled_answers.append(zz['artist'])
            shuffle(display_shuffled_answers)
            create_question(
                question_type=answer_column,
                ask_question=choice(ask_questions),
                present_answer=choice(present_answers),
                acceptable_answers=[the_right_answer['artist']],
                wrong_answers=[display_shuffled_answers, present_answer_data])
        db.session.commit()

def which_is_djs_favorite_album():
    dj_id_pool = playlists.get_all_dj_ids()
    random_dj_ids = choices(dj_id_pool, k=SEED_QUESTION_COUNT)
    for dj_id in random_dj_ids:
        resultproxy = playlist_tracks.get_favorite_albums(dj_id=dj_id, reverse=True, min_plays=5)
        answer_key = common.unpack_a_result_proxy(resultproxy=resultproxy)
        try:
            air_name = playlists.get_airname(dj_id)
        except AttributeError:
            continue  # Dudd DJ.
        if len(answer_key) < 20:
            continue  # Dudd DJ.
        answer_column = "album_title"
        winners = answer_key[:10]
        losers = answer_key[10:]
        for the_right_answer in winners:
            ask_questions = [
                f"Which does {air_name} play most?", f"Which album is {air_name}'s favorite?",
                f"Which album has {air_name} played the most?"]
            present_answers = [
                f"{air_name} likes this album the most:", f"{air_name} has played this album the most:",
                f"This album is played by {air_name} a lot:"]
            three_wrong_answers = choices(losers, k=3)
            answer_pile = [the_right_answer] + three_wrong_answers
            present_answer_data = []
            display_shuffled_answers = []
            for zz in sorted(answer_pile, key=itemgetter('plays'), reverse=True):
                present_answer_data.append([zz[answer_column], zz['plays']])
                display_shuffled_answers.append(zz[answer_column])
            shuffle(display_shuffled_answers)
            create_question(
                question_type=answer_column,
                ask_question=choice(ask_questions),
                present_answer=choice(present_answers),
                acceptable_answers=[the_right_answer[answer_column]],
                wrong_answers=[display_shuffled_answers, present_answer_data])
        db.session.commit()

def which_is_djs_favorite_track():
    dj_id_pool = playlists.get_all_dj_ids()
    random_dj_ids = choices(dj_id_pool, k=SEED_QUESTION_COUNT)
    for dj_id in random_dj_ids:
        resultproxy = playlist_tracks.get_favorite_tracks(dj_id=dj_id, reverse=True, min_plays=5)
        answer_key = common.unpack_a_result_proxy(resultproxy=resultproxy)
        try:
            air_name = playlists.get_airname(dj_id)
        except AttributeError:
            continue  # Dudd DJ.
        if len(answer_key) < 20:
            continue  # Dudd DJ.
        answer_column = "track_title"
        winners = answer_key[:10]
        losers = answer_key[10:]
        for the_right_answer in winners:
            ask_questions = [
                f"Which track did {air_name} play most?", f"Which track is {air_name}'s favorite?",
                f"Which track has {air_name} played the most?"]
            present_answers = [
                f"{air_name} likes this one the most:", f"{air_name} has played this track the most:",
                f"This song is played by {air_name} a lot:"]
            three_wrong_answers = choices(losers, k=3)
            answer_pile = [the_right_answer] + three_wrong_answers
            present_answer_data = []
            display_shuffled_answers = []
            for zz in sorted(answer_pile, key=itemgetter('plays'), reverse=True):
                present_answer_data.append([zz[answer_column], zz['plays']])
                display_shuffled_answers.append(zz[answer_column])
            shuffle(display_shuffled_answers)
            create_question(
                question_type=answer_column,
                ask_question=choice(ask_questions),
                present_answer=choice(present_answers),
                acceptable_answers=[the_right_answer[answer_column]],
                wrong_answers=[display_shuffled_answers, present_answer_data])
        db.session.commit()

def top_ten_artist():
    resultproxy = playlist_tracks.get_top10_artists(start_date, end_date, n=10)
    question_type = "artist"
    ask_questions = [
        f"Who appeared in the top ten during the week of {start_date}?",
        f"Which artist was in the top 10 in {start_date}?",
        f"During the week of {start_date}, which artist was in the top ten?"]
    present_answers = [
        f"This artist appeared in the top ten during the week of {start_date}:",
        f"This artist was in the top 10 in {start_date}:",
        f"During the week of {start_date}, this artist was in the top ten:"]
        
def top_ten_album():
    resultproxy = playlist_tracks.get_top10_albums(start_date, end_date, n=10)
    question_type = "album"
    ask_questions = [
        f"Who appeared in the top ten during the week of {start_date}?",
        f"Which album was in the top 10 in {start_date}?",
        f"During the week of {start_date}, which album was in the top ten?"]
    present_answers = [
        f"This album appeared in the top ten during the week of {start_date}:",
        f"This album was in the top 10 in {start_date}:",
        f"During the week of {start_date}, this album was in the top ten:"]

def top_ten_track():
    resultproxy = playlist_tracks.get_top10_tracks(start_date, end_date, n=10)
    question_type = "track"
    ask_questions = [
        f"Who appeared in the top ten during the week of {start_date}?",
        f"Which track was in the top 10 in {start_date}?",
        f"During the week of {start_date}, which track was in the top ten?"]
    present_answers = [
        f"This track appeared in the top ten during the week of {start_date}:",
        f"This track was in the top 10 in {start_date}:",
        f"During the week of {start_date}, this track was in the top ten:"]

def last_play_of_artist():
    resultproxy = playlist_tracks.get_last_play_of_artist(artist, reverse=False)
    question_type = "artist"
    ask_questions = [
        f"When was the last time we played {artist}?",
        f"When was the last play of {artist} on KFJC?",
        f"When was the last time {artist} was played?"]
    present_answers = [
        f"This is the last time we played {artist}:",
        f"The last play of {artist} on KFJC was:",
        f"The last time {artist} was played was:"]

def last_play_of_album():
    resultproxy = playlist_tracks.get_last_play_of_album(album, reverse=False)
    question_type = "album"
    ask_questions = [
        f"When was the last time we played {album}?",
        f"When was the last play of {album} on KFJC?",
        f"When was the last time {album} was played?"]
    present_answers = [
        f"This is the last time we played {album}:",
        f"The last play of {album} on KFJC was:",
        f"The last time {album} was played was:"]

def last_play_of_track():
    resultproxy = playlist_tracks.get_last_play_of_track(track, reverse=False)
    question_type = "track"
    ask_questions = [
        f"When was the last time we played {track}?",
        f"When was the last play of {track} on KFJC?",
        f"When was the last time {track} was played?"]
    present_answers = [
        f"This is the last time we played {track}:",
        f"The last play of {track} on KFJC was:",
        f"The last time {track} was played was:"]

def tracks_on_an_album():
    # get 20 random albums with at least 9 tracks.
    resultproxy = tracks.get_tracks_by_kfjc_album_id(kfjc_album_id)

    album = Album.query.get(kfjc_album_id)
    
    question_type = "track"
    ask_questions = [
        f"Name a track from the album {album.title}:",
        f"Can you pick the track that's from the {album.title} album?",
        f"Pick the track that's off the album {album.title}:"]
    present_answers = [
        f"This track is from the album {album.title}:",
        f"Here's a track that's from the {album.title} album:",
        f"{album.title} contains these tracks:"]
        
def when_was_dj_last_on_the_air():
    answer_key = playlists.get_djs_by_last_show(reverse=False)
    dj_id_pool = playlists.get_all_dj_ids()
    random_dj_ids = choices(dj_id_pool, k=SEED_QUESTION_COUNT)
    random_date_surrounding_another_date()

# -=-=-=-=-=-=-=-=-=-=-=- Make Fake Answers -=-=-=-=-=-=-=-=-=-=-=-

def random_number_within_percent(target_number, percent=40, k=1):
    """Make convincing fake answers for number questions."""
    high_value = int(target_number * (1 + (percent / 100)))
    low_value = int(target_number * (1 - (percent / 100)))
    if k != 1:
        random_numbers = []
        for _ in range(k):
            random_numbers.append(randrange(low_value, high_value))
        return random_numbers
    else:
        return randrange(low_value, high_value)

def random_date_surrounding_another_date(target_date_time, k=1):
    """Forget the time... just return a date."""
    
    days_from_now = (date.today() - date.fromisoformat(target_date_time[:10])).days
    
    random_days = random_number_within_percent(target_number=days_from_now, percent=20, k=k)
    
    random_dates = []
    for dd in random_days:
        random_dates.append(common.make_date_pretty(date_time_string=(
            datetime.now() - timedelta(days=dd))))
    return random_dates

# -=-=-=-=-=-=-=-=-=-=-=- Choose Random Question -=-=-=-=-=-=-=-=-=-=-=-

def get_unique_question(user_id):
    """TODO"""
    users_answers = Answer.query.filter(Answer.user_id == user_id).all()
    user_already_answered = [users_answer.question_id for users_answer in users_answers]
    question_ids = [one_question.question_id for one_question in Question.query.all()]
    allowed_pool = list(set(question_ids) - set(user_already_answered))
    if not allowed_pool:
        return  # You've answered all the questions!
    
    random_question_id = choice(allowed_pool)
    return get_question_by_id(question_id=random_question_id)
    

if __name__ == '__main__':
    """Will connect you to the database when you run questions.py interactively"""
    from server import app
    connect_to_db(app)
