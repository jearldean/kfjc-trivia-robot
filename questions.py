"""Question operations for KFJC Trivia Robot."""

from datetime import datetime, timedelta, date
import time
from operator import attrgetter
from random import randrange, choice, choices, shuffle
from sqlalchemy import exc
from psycopg2 import errors

from model import Answer, PlaylistTrack, db, connect_to_db, Question
import albums
import playlists
import playlist_tracks
import tracks
import common

SEED_QUESTION_COUNT = 30

def create_question(
    question_type, ask_question, present_answer, acceptable_answers,
    display_shuffled_answers, present_answer_data_headings, present_answer_data):
    """Create and return a new question."""

    question = Question(
        question_type=question_type,
        ask_question=ask_question,
        present_answer=present_answer,
        acceptable_answers=acceptable_answers,
        display_shuffled_answers=display_shuffled_answers,
        present_answer_data_headings=present_answer_data_headings,
        present_answer_data=present_answer_data)

    db.session.add(question)
    # Don't forget to call model.db.session.commit() when done adding items.

    return question

def get_question_by_id(question_id):
    """Return a question by question_id."""

    return Question.query.get(question_id)
     
# -=-=-=-=-=-=-=-=-=-=-=- Choose Random Question -=-=-=-=-=-=-=-=-=-=-=-

def get_unique_question(user_id):
    """Pose a question to the user that they have not answered before."""

    users_answers = Answer.query.filter(Answer.user_id == user_id).all()
    user_already_answered = [users_answer.question_id for users_answer in users_answers]
    question_ids = [one_question.question_id for one_question in Question.query.all()]
    allowed_pool = list(set(question_ids) - set(user_already_answered))
    if not allowed_pool:
        return  # You've answered all the questions!
    
    random_question_id = choice(allowed_pool)
    return get_question_by_id(question_id=random_question_id)

# -=-=-=-=-=-=-=-=-=-=-=- Seed Questions Table -=-=-=-=-=-=-=-=-=-=-=-

def make_all_questions():
    """Create SEED_QUESTION_COUNT questions for 16 question types.
    
    Creates 640 questions in 10 mins."""
    tic = time.perf_counter()
    who_is_the_oldest_dj()
    who_is_the_newest_dj()
    who_has_the_most_shows()
    when_was_dj_last_on_the_air()
    which_is_djs_favorite_artist()
    which_is_djs_favorite_album()
    which_is_djs_favorite_track()
    top_ten_artist()
    top_ten_album()
    top_ten_track()
    albums_by_an_artist()
    artist_of_an_album()
    tracks_on_an_album()
    last_play_of_artist()
    last_play_of_album()
    last_play_of_track()
    toc = time.perf_counter()
    mins = float((toc - tic)/60)
    print(
        f"Seeding Questions took {mins:0.4f} minutes "
        "using SEED_QUESTION_COUNT={SEED_QUESTION_COUNT}.")

def who_is_the_oldest_dj():
    """TODO: All these methods are woefully bloated and in need of consolidation."""
    results_named_tuple = playlists.get_djs_by_first_show(reverse=False)
    question_type = "A Question about DJs:"
    ask_questions = [
        "From these choices, who was on the air first?",
        "Out of these four, who was first on the air?",
        "Who was a DJ before any of the other choices?",
        "Pick the DJ who came on KFJC before the others:"]
    present_answers = [
        "This person was on the air first:", "This person hit the airwaves first:",
        "This DJ was first on the air:"]
    search_key = 'firstshow'
    reverse_display_answers = False

    winners = results_named_tuple[:SEED_QUESTION_COUNT]  # list of dicts
    losers = results_named_tuple[SEED_QUESTION_COUNT:]
    for the_right_answer in winners:
        three_wrong_answers = choices(losers, k=3)
        answer_pile = [the_right_answer] + three_wrong_answers
        present_answer_data = []
        display_shuffled_answers = []

        present_answer_data_headings=["Air Name", "Last Show"]
        for zz in sorted(answer_pile, key=attrgetter(search_key), reverse=reverse_display_answers):
            item_value = common.make_date_pretty(date_time_string=zz.lastshow)
            present_answer_data.append([zz.air_name, item_value])
            display_shuffled_answers.append(zz.air_name)
            
        acceptable_answers = [display_shuffled_answers[0]]
        shuffle(display_shuffled_answers)
        create_question(
            question_type=question_type,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answers=acceptable_answers,
            display_shuffled_answers=display_shuffled_answers,
            present_answer_data_headings=present_answer_data_headings,
            present_answer_data=present_answer_data)

    db.session.commit()

def who_is_the_newest_dj():
    """TODO: All these methods are woefully bloated and in need of consolidation."""
    results_named_tuple = playlists.get_djs_by_first_show(reverse=True)
    question_type = "A Question about DJs:"
    ask_questions = [
        "From these choices, who is the newest KFJC DJ?",
        "Out of these four, who was last to appear on the air?",
        "Pick the rookie! Who was a DJ last out of any of the other choices?",
        "Spot the greenhorn! Pick the DJ who came on KFJC most recently:"]
    present_answers = [
        "This person is the most recent DJ:", "This person is newest to our airwaves:",
        "Here's the newest DJ from that lot:", "Our newest DJ is:"]
    search_key = 'firstshow'
    reverse_display_answers = True
    
    winners = results_named_tuple[:SEED_QUESTION_COUNT]  # list of dicts
    losers = results_named_tuple[SEED_QUESTION_COUNT:]
    for the_right_answer in winners:
        three_wrong_answers = choices(losers, k=3)
        answer_pile = [the_right_answer] + three_wrong_answers
        present_answer_data = []
        display_shuffled_answers = []

        present_answer_data_headings=["Air Name", "First Show"]
        for zz in sorted(answer_pile, key=attrgetter(search_key), reverse=reverse_display_answers):
            item_value = common.make_date_pretty(date_time_string=zz.firstshow)
            present_answer_data.append([zz.air_name, item_value])
            display_shuffled_answers.append(zz.air_name)
            
        acceptable_answers = [display_shuffled_answers[0]]
        shuffle(display_shuffled_answers)
        create_question(
            question_type=question_type,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answers=acceptable_answers,
            display_shuffled_answers=display_shuffled_answers,
            present_answer_data_headings=present_answer_data_headings,
            present_answer_data=present_answer_data)

    db.session.commit()

def who_has_the_most_shows():
    """TODO: All these methods are woefully bloated and in need of consolidation."""
    results_named_tuple = playlists.get_djs_by_show_count()
    question_type = "A Question about DJs:"
    ask_questions = [
        "Who has the most shows?", "Who has done the most shows?",
        "Which DJ has the most shows?"]
    present_answers = [
        "This person has done the most shows:", "This person has the most shows:",
        "This DJ has more shows:"]
    search_key = 'showcount'
    reverse_display_answers = True
    
    winners = results_named_tuple[:SEED_QUESTION_COUNT]  # list of dicts
    losers = results_named_tuple[SEED_QUESTION_COUNT:]
    for the_right_answer in winners:
        three_wrong_answers = choices(losers, k=3)
        answer_pile = [the_right_answer] + three_wrong_answers
        present_answer_data = []
        display_shuffled_answers = []

        for zz in sorted(answer_pile, key=attrgetter(search_key), reverse=reverse_display_answers):
            item_value = common.format_an_int_with_commas(your_int=zz.showcount)
            present_answer_data.append([zz.air_name, item_value])
            display_shuffled_answers.append(zz.air_name)
        present_answer_data_headings=["Air Name", "Show Count"]
            
        acceptable_answers = [display_shuffled_answers[0]]
        shuffle(display_shuffled_answers)
        create_question(
            question_type=question_type,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answers=acceptable_answers,
            display_shuffled_answers=display_shuffled_answers,
            present_answer_data_headings=present_answer_data_headings,
            present_answer_data=present_answer_data)

    db.session.commit()

def when_was_dj_last_on_the_air():
    """TODO: All these methods are woefully bloated and in need of consolidation."""
    results_named_tuple = playlists.get_djs_by_last_show(reverse=False)
    random_last_shows = choices(results_named_tuple, k=SEED_QUESTION_COUNT)
    question_type = "A Question about DJs:"
    for last_show in random_last_shows:
        the_right_answer = last_show.lastshow  # A Datetime Object.
        three_wrong_answers = random_date_surrounding_another_date(the_right_answer, k=3)
        the_pretty_right_answer = common.make_date_pretty(date_time_string=the_right_answer)
        answer_pile = [the_pretty_right_answer] + three_wrong_answers
        air_name = last_show.air_name
        ask_questions = [
            f"Can you guess when {air_name} played their last show?",
            f"When was {air_name} last on the air?",
            f"When was {air_name}'s last show?"]
        present_answers = [
            f"{air_name} was last on the air:",
            f"This is when {air_name} last did a show:",
            f"This is the last time we heard {air_name} on the air:"]
        present_answer_data = [[the_pretty_right_answer, ""]]  # Only one row.
        shuffle(answer_pile)
        create_question(
            question_type=question_type,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answers=[the_pretty_right_answer],
            display_shuffled_answers=answer_pile,
            present_answer_data_headings=["", ""],  # No headings. One-sentence answer.
            present_answer_data=present_answer_data)

    db.session.commit()

def which_is_djs_favorite_artist():
    """TODO: All these methods are woefully bloated and in need of consolidation."""
    question_type = "A Question about Artists:"
    dj_id_pool = playlists.get_all_dj_ids()
    random_dj_ids = choices(dj_id_pool, k=SEED_QUESTION_COUNT)
    for dj_id in random_dj_ids:
        answer_key = playlist_tracks.get_favorite_artists(dj_id=dj_id, reverse=True, min_plays=5)
        try:
            air_name = playlists.get_airname(dj_id)
        except AttributeError:
            continue  # Dudd DJ.
        if len(answer_key) < 20:
            continue  # Dudd DJ.
        
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
            for zz in sorted(answer_pile, key=attrgetter('plays'), reverse=True):
                present_answer_data.append([zz.artist, zz.plays])
                display_shuffled_answers.append(zz.artist)
            shuffle(display_shuffled_answers)
            create_question(
                question_type=question_type,
                ask_question=choice(ask_questions),
                present_answer=choice(present_answers),
                acceptable_answers=[the_right_answer.artist],
                display_shuffled_answers=display_shuffled_answers,
                present_answer_data_headings=["Artist", "Plays"],
                present_answer_data=present_answer_data)
                
        db.session.commit()

def which_is_djs_favorite_album():
    """TODO: All these methods are woefully bloated and in need of consolidation."""
    question_type = "A Question about Albums:"
    dj_id_pool = playlists.get_all_dj_ids()
    random_dj_ids = choices(dj_id_pool, k=SEED_QUESTION_COUNT)
    for dj_id in random_dj_ids:
        answer_key = playlist_tracks.get_favorite_albums(dj_id=dj_id, reverse=True, min_plays=5)
        try:
            air_name = playlists.get_airname(dj_id)
        except AttributeError:
            continue  # Dudd DJ.
        if len(answer_key) < 20:
            continue  # Dudd DJ.
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
            for zz in sorted(answer_pile, key=attrgetter('plays'), reverse=True):
                present_answer_data.append([zz.album_title, zz.plays])
                display_shuffled_answers.append(zz.album_title)
            shuffle(display_shuffled_answers)
            create_question(
                question_type=question_type,
                ask_question=choice(ask_questions),
                present_answer=choice(present_answers),
                acceptable_answers=[the_right_answer.album_title],
                display_shuffled_answers=display_shuffled_answers,
                present_answer_data_headings=["Album", "Plays"],
                present_answer_data=present_answer_data)
                
        db.session.commit()

def which_is_djs_favorite_track():
    """TODO: All these methods are woefully bloated and in need of consolidation."""
    question_type = "A Question about Tracks:"
    dj_id_pool = playlists.get_all_dj_ids()
    random_dj_ids = choices(dj_id_pool, k=SEED_QUESTION_COUNT)
    for dj_id in random_dj_ids:
        answer_key = playlist_tracks.get_favorite_tracks(dj_id=dj_id, reverse=True, min_plays=5)
        try:
            air_name = playlists.get_airname(dj_id)
        except AttributeError:
            continue  # Dudd DJ.
        if len(answer_key) < 20:
            continue  # Dudd DJ.
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
            for zz in sorted(answer_pile, key=attrgetter('plays'), reverse=True):
                present_answer_data.append([zz.track_title, zz.plays])
                display_shuffled_answers.append(zz.track_title)
            shuffle(display_shuffled_answers)
            create_question(
                question_type=question_type,
                ask_question=choice(ask_questions),
                present_answer=choice(present_answers),
                acceptable_answers=[the_right_answer.track_title],
                display_shuffled_answers=display_shuffled_answers,
                present_answer_data_headings=["Track", "Plays"],
                present_answer_data=present_answer_data)
                
        db.session.commit()

def top_ten_artist():
    """TODO: All these methods are woefully bloated and in need of consolidation."""
    old, _ = common.get_ages(PlaylistTrack.time_played)
    # I improved this to go back to 1995-09-19.
    days_to_choose_from = (datetime.now() - old).days
    random_days_before_today = choices(range(days_to_choose_from), k=SEED_QUESTION_COUNT)
    for random_days in random_days_before_today:
        start_date = date.today() - timedelta(days=random_days) 
        end_date = date.today() - timedelta(days=(random_days - 7)) # During a Week.
        answer_key = playlist_tracks.get_top10_artists(start_date, end_date, n=40)
        if len(answer_key) == 0:
            continue  # Dud list. Playlist Track data is only good after 2011.
        # But I have an idea on how to estimate more cells.
        question_type = "A Question about an Artist:"
        pretty_date = common.make_date_pretty(start_date)
        ask_questions = [
            f"Who appeared in the TopTen during the week of {pretty_date}?",
            f"Which artist was in the weekly Top10 in {pretty_date}?",
            f"All of these artists were in the Top40 during the week of {pretty_date} but which one made the Top10?",
            f"All these artists were in the Top40 during the week of {pretty_date}. Which Artist was in the Top10?",
            f"During the week of {pretty_date}, which artist was in the Top Ten?"]
        present_answers = [
            f"Here is the Top40 by Artist during the week of {pretty_date}:",
            f"These were the Top40 Artists on {pretty_date}:",
            f"During the week of {pretty_date}, these are the Top40 Artists:"]
        winners = answer_key[:10]  # Top Ten
        one_winner = choice(winners)
        losers = answer_key[10:]  # Bottom 30
        three_wrong_answers = choices(losers, k=3)
        answer_pile = [one_winner] + three_wrong_answers
        present_answer_data = []
        display_shuffled_answers = []
        for zz in sorted(answer_key, key=attrgetter('plays'), reverse=True):
            present_answer_data.append([zz.artist, zz.plays])
        for zz in sorted(answer_pile, key=attrgetter('plays'), reverse=True):
            display_shuffled_answers.append(zz.artist)
        shuffle(display_shuffled_answers)
        create_question(
            question_type=question_type,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answers=[one_winner.artist],
            display_shuffled_answers=display_shuffled_answers,
            present_answer_data_headings=["Who played what", "Plays"],
            present_answer_data=present_answer_data)
            
    db.session.commit()
        
def top_ten_album():
    """TODO: All these methods are woefully bloated and in need of consolidation."""
    old, _ = common.get_ages(PlaylistTrack.time_played)
    # I improved this to go back to 1995-09-19.
    days_to_choose_from = (datetime.now() - old).days
    random_days_before_today = choices(range(days_to_choose_from), k=SEED_QUESTION_COUNT)
    for random_days in random_days_before_today:
        start_date = date.today() - timedelta(days=random_days) 
        end_date = date.today() - timedelta(days=(random_days - 7)) # During a Week.
        answer_key = playlist_tracks.get_top10_albums(start_date, end_date, n=40)
        if len(answer_key) == 0:
            continue  # Dud list. Playlist Track data is only good after 2011.
        # But I have an idea on how to estimate more cells.
        question_type = "A Question about an Album:"
        pretty_date = common.make_date_pretty(start_date)
        ask_questions = [
            f"Which album appeared in the TopTen during the week of {pretty_date}?",
            f"Which album was in the weekly Top10 in {pretty_date}?",
            f"All of these albums were in the Top40 during the week of {pretty_date} but which one made the Top10?",
            f"All these albums were in the Top40 during the week of {pretty_date}. Which Album was in the Top10?",
            f"During the week of {pretty_date}, which album was in the Top Ten?"]
        present_answers = [
            f"Here is the Top40 by Album during the week of {pretty_date}:",
            f"These were the Top40 Albums on {pretty_date}:",
            f"During the week of {pretty_date}, these are the Top40 Albums:"]
        winners = answer_key[:10]  # Top Ten
        one_winner = choice(winners)
        losers = answer_key[10:]  # Bottom 30
        three_wrong_answers = choices(losers, k=3)
        answer_pile = [one_winner] + three_wrong_answers
        present_answer_data = []
        display_shuffled_answers = []
        for zz in sorted(answer_key, key=attrgetter('plays'), reverse=True):
            present_answer_data.append([zz.album_title, zz.plays])
        for zz in sorted(answer_pile, key=attrgetter('plays'), reverse=True):
            display_shuffled_answers.append(zz.album_title)
        shuffle(display_shuffled_answers)
        create_question(
            question_type=question_type,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answers=[one_winner.album_title],
            display_shuffled_answers=display_shuffled_answers,
            present_answer_data_headings=["Who played what", "Plays"],
            present_answer_data=present_answer_data)
            
    db.session.commit()

def top_ten_track():
    """TODO: All these methods are woefully bloated and in need of consolidation."""
    old, _ = common.get_ages(PlaylistTrack.time_played)
    # I improved this to go back to 1995-09-19.
    days_to_choose_from = (datetime.now() - old).days
    random_days_before_today = choices(range(days_to_choose_from), k=SEED_QUESTION_COUNT)
    for random_days in random_days_before_today:
        start_date = date.today() - timedelta(days=random_days) 
        end_date = date.today() - timedelta(days=(random_days - 7)) # During a Week.
        answer_key = playlist_tracks.get_top10_tracks(start_date, end_date, n=40)
        if len(answer_key) == 0:
            continue  # Dud list. Playlist Track data is only good after 2011.
        # But I have an idea on how to estimate more cells.
        question_type = "A Question about a Track:"
        pretty_date = common.make_date_pretty(start_date)
        ask_questions = [
            f"Which track appeared in the TopTen during the week of {pretty_date}?",
            f"Which track was in the weekly Top10 in {pretty_date}?",
            f"All of these tracks were in the Top40 during the week of {pretty_date} but which one made the Top10?",
            f"All these tracks were in the Top40 during the week of {pretty_date}. Which Track was in the Top10?",
            f"During the week of {pretty_date}, which track was in the Top Ten?"]
        present_answers = [
            f"Here is the Top40 by Track during the week of {pretty_date}:",
            f"These were the Top40 Tracks on {pretty_date}:",
            f"During the week of {pretty_date}, these are the Top40 Tracks:"]
        winners = answer_key[:10]  # Top Ten
        one_winner = choice(winners)
        losers = answer_key[10:]  # Bottom 30
        three_wrong_answers = choices(losers, k=3)
        answer_pile = [one_winner] + three_wrong_answers
        present_answer_data = []
        display_shuffled_answers = []
        for zz in sorted(answer_key, key=attrgetter('plays'), reverse=True):
            present_answer_data.append([zz.track_title, zz.plays])
        for zz in sorted(answer_pile, key=attrgetter('plays'), reverse=True):
            display_shuffled_answers.append(zz.track_title)
        shuffle(display_shuffled_answers)
        create_question(
            question_type=question_type,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answers=[one_winner.track_title],
            display_shuffled_answers=display_shuffled_answers,
            present_answer_data_headings=["Who played what", "Plays"],
            present_answer_data=present_answer_data)

        db.session.commit()

def get_four_random_albums():
    """TODO: All these methods are woefully bloated and in need of consolidation."""
    four_random_albums = []
    for _ in range(4):
        # Get 4 random albums:
        random_kfjc_album_id = playlist_tracks.get_a_random_kfjc_album_id()
        random_album = albums.get_album_by_id(kfjc_album_id=random_kfjc_album_id)
        four_random_albums.append(random_album)
    return four_random_albums

def albums_by_an_artist():
    """Formulate a question about albums by an artist.
    
    TODO: All these methods are woefully bloated and in need of consolidation."""
    question_type = "A Question about an Album:"
    for _ in range(SEED_QUESTION_COUNT):
        four_random_albums = get_four_random_albums()
        # The first album shall be the winner:
        winner_artist = four_random_albums[0].artist
        winner_album_title = four_random_albums[0].title
        ask_questions = [
            f"Which album is by the artist {winner_artist}?",
            f"Can you pick the album that's from {winner_artist}?",
            f"Which album did {winner_artist} make?"]
        present_answers = [
            f"This album is from {winner_artist}:",
            f"This album is by {winner_artist}:",
            f"{winner_artist} made this album:"]

        album_titles = [album.title for album in four_random_albums]
        shuffle(album_titles)
        present_answer_data = [[album.artist, album.title] for album in four_random_albums]
        if present_answer_data:  # Null Spike Jones title made it in there.
            create_question(
                question_type=question_type,
                ask_question=choice(ask_questions),
                present_answer=choice(present_answers),
                acceptable_answers=[winner_album_title],
                display_shuffled_answers=album_titles,
                present_answer_data_headings=["Artist", "Album"],
                present_answer_data=present_answer_data)
                    
    db.session.commit()
        
def artist_of_an_album():
    """Formulate a question about artist of an album.
    
    TODO: All these methods are woefully bloated and in need of consolidation."""
    question_type = "A Question about an Artist:"
    for _ in range(SEED_QUESTION_COUNT):
        four_random_albums = get_four_random_albums()
        # The first album shall be the winner:
        winner_artist = four_random_albums[0].artist
        winner_album_title = four_random_albums[0].title
        ask_questions = [
            f"Which artist made the album {winner_album_title}?",
            f"Can you pick the artist that's made {winner_album_title}?",
            f"Name the artist of {winner_album_title}?"]
        present_answers = [
            f"This album is from {winner_album_title}:",
            f"This album is by {winner_album_title}:",
            f"{winner_album_title} made this album:"]

        album_artists = [album.artist for album in four_random_albums]
        shuffle(album_artists)
        present_answer_data = [[album.artist, album.title] for album in four_random_albums]
        if present_answer_data:  # Null Spike Jones title made it in there.
            create_question(
                question_type=question_type,
                ask_question=choice(ask_questions),
                present_answer=choice(present_answers),
                acceptable_answers=[winner_artist],
                display_shuffled_answers=album_artists,
                present_answer_data_headings=["Artist", "Album"],
                present_answer_data=present_answer_data)
                    
    db.session.commit()

def tracks_on_an_album():
    """Formulate a question about tracks on an album.
    
    TODO: All these methods are woefully bloated and in need of consolidation."""
    question_type = "A Question about a Track:"
    for _ in range(SEED_QUESTION_COUNT):
        four_random_albums = get_four_random_albums()
        # The first album shall be the winner:
        winner_artist = four_random_albums[0].artist
        winner_album_title = four_random_albums[0].title
        artist_posessive = winner_artist + common.the_right_apostrophe(winner_artist)
        ask_questions = [
            f"Name a track from {artist_posessive} album {winner_album_title}:",
            f"Can you pick the track that's from {artist_posessive} {winner_album_title} album?",
            f"Pick the track that's off {artist_posessive} album {winner_album_title}:"]
        present_answers = [
            f"This track is from the {artist_posessive} album {winner_album_title}:",
            f"Here's a track that's from {artist_posessive} {winner_album_title} album:",
            f"{artist_posessive} {winner_album_title} contains these tracks:"]

        answer_pile = []
        present_answer_data = []
        for each_album in four_random_albums:
            album_tracks = tracks.get_tracks_by_kfjc_album_id(
                kfjc_album_id=each_album.kfjc_album_id)
            random_track = choice(album_tracks)
            answer_pile.append(random_track.title)
            present_answer_data.append([each_album.artist, random_track.title])
        shuffle(answer_pile)
    
        create_question(
            question_type=question_type,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answers=[winner_artist],
            display_shuffled_answers=answer_pile,
            present_answer_data_headings=["Artist", "Track"],
            present_answer_data=present_answer_data)
                    
    db.session.commit()

def last_play_of_artist():
    """Create a question about the last time an Artist was played.
    
    TODO: All these methods are woefully bloated and in need of consolidation."""
    question_type = "A Question about an Artist:"
    for _ in range(SEED_QUESTION_COUNT):
        random_artist = playlist_tracks.get_a_random_artist()
        ask_questions = [
            f"When was the last time we played the Artist '{random_artist}'?",
            f"When was the last play of the Artist '{random_artist}' on KFJC?",
            f"When was the last time the Artist '{random_artist}' was played?"]
        present_answers = [
            f"This is the last time we played the Artist '{random_artist}':",
            f"The last play of the Artist '{random_artist}' on KFJC was:",
            f"The last time the Artist '{random_artist}' was played was:"]
        try:
            answer_key = playlist_tracks.get_last_play_of_artist(
                artist=random_artist, reverse=False)
        except exc.ProgrammingError:
            continue  # TODO Spare apostrophes are getting in the way of lookup.
        except errors.InFailedSqlTransaction:
            continue
        except exc.InternalError:  # Forget it, move on.
            continue

        try:
            winner = answer_key[0]  # First Hit
        except IndexError:
            continue  # Might get a dud, an artist before 2011 with no valid time_played.
        except AttributeError:
            continue  # NoneType
        # p.air_name, pt.artist, pt.album_title, pt.track_title, pt.time_played
        the_right_answer = winner.time_played
        three_wrong_answers = random_date_surrounding_another_date(the_right_answer, k=3)
        the_pretty_right_answer = common.make_date_pretty(date_time_string=the_right_answer)
        answer_pile = [the_pretty_right_answer] + three_wrong_answers
        shuffle(answer_pile)
        present_answer_data = []
        for zz in answer_key:
            air_name = zz.air_name
            track_title = zz.track_title
            pretty_date = common.make_date_pretty(date_time_string=zz.time_played)
            present_answer_data.append([f"{air_name} played {track_title}", pretty_date])
        create_question(
            question_type=question_type,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answers=[the_pretty_right_answer],
            display_shuffled_answers=answer_pile,
            present_answer_data_headings=["Who played what", "Date"],
            present_answer_data=present_answer_data)
        
    db.session.commit()

def last_play_of_album():
    """Create a question about the last time at Album was played.
    
    TODO: All these methods are woefully bloated and in need of consolidation."""
    question_type = "A Question about an Album:"
    for _ in range(SEED_QUESTION_COUNT):
        random_album = playlist_tracks.get_a_random_album()
        if not random_album:
            continue
        ask_questions = [
            f"When was the last time we played the Album '{random_album}'?",
            f"When was the last play of the Album '{random_album}' on KFJC?",
            f"When was the last time the Album '{random_album}' was played?"]
        present_answers = [
            f"This is the last time we played the Album '{random_album}':",
            f"The last play of the Album '{random_album}' on KFJC was:",
            f"The last time the Album '{random_album}' was played was:"]
        try:
            answer_key = playlist_tracks.get_last_play_of_album(
                album=random_album, reverse=False)
        except exc.ProgrammingError:
            continue  # TODO Spare apostrophes are getting in the way of lookup.
        except errors.InFailedSqlTransaction:
            continue
        except exc.InternalError:  # Forget it, move on.
            continue

        try:
            winner = answer_key[0]  # First Hit
        except IndexError:
            continue  # Might get a dud, an artist before 2011 with no valid time_played.
        except AttributeError:
            continue  # NoneType
        # p.air_name, pt.artist, pt.album_title, pt.track_title, pt.time_played
        the_right_answer = winner.time_played
        three_wrong_answers = random_date_surrounding_another_date(the_right_answer, k=3)
        the_pretty_right_answer = common.make_date_pretty(date_time_string=the_right_answer)
        answer_pile = [the_pretty_right_answer] + three_wrong_answers
        shuffle(answer_pile)
        present_answer_data = []
        for zz in answer_key:
            air_name = zz.air_name
            track_title = zz.track_title
            pretty_date = common.make_date_pretty(date_time_string=zz.time_played)
            present_answer_data.append([f"{air_name} played {track_title}", pretty_date])
        create_question(
            question_type=question_type,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answers=[the_pretty_right_answer],
            display_shuffled_answers=answer_pile,
            present_answer_data_headings=["Who played what", "Date"],
            present_answer_data=present_answer_data)
        
    db.session.commit()

def last_play_of_track():
    """Create a question about the last time at Track was played.
    
    TODO: All these methods are woefully bloated and in need of consolidation."""
    question_type = "A Question about a Track:"
    for _ in range(SEED_QUESTION_COUNT):
        random_track = playlist_tracks.get_a_random_track()
        if not random_track:
            continue
        ask_questions = [
            f"When was the last time we played the Track '{random_track}'?",
            f"When was the last play of the Track '{random_track}' on KFJC?",
            f"When was the last time the Track '{random_track}' was played?"]
        present_answers = [
            f"This is the last time we played the Track '{random_track}':",
            f"The last play of the Track '{random_track}' on KFJC was:",
            f"The last time the Track '{random_track}' was played was:"]
        try:
            answer_key = playlist_tracks.get_last_play_of_track(
                track=random_track, reverse=False)
        except exc.ProgrammingError:
            continue  # TODO Spare apostrophes are getting in the way of lookup.
        except errors.InFailedSqlTransaction:
            continue
        except exc.InternalError:  # Forget it, move on.
            continue

        try:
            winner = answer_key[0]  # First Hit
        except IndexError:
            continue  # Might get a dud, an artist before 2011 with no valid time_played.
        except AttributeError:
            continue  # NoneType
        # p.air_name, pt.artist, pt.album_title, pt.track_title, pt.time_played
        the_right_answer = winner.time_played
        three_wrong_answers = random_date_surrounding_another_date(the_right_answer, k=3)
        the_pretty_right_answer = common.make_date_pretty(date_time_string=the_right_answer)
        answer_pile = [the_pretty_right_answer] + three_wrong_answers
        shuffle(answer_pile)
        present_answer_data = []
        for zz in answer_key:
            air_name = zz.air_name
            track_title = zz.track_title
            pretty_date = common.make_date_pretty(date_time_string=zz.time_played)
            present_answer_data.append([f"{air_name} played {track_title}", pretty_date])
        create_question(
            question_type=question_type,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answers=[the_pretty_right_answer],
            display_shuffled_answers=answer_pile,
            present_answer_data_headings=["Who played what", "Date"],
            present_answer_data=present_answer_data)
        
    db.session.commit()

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
    
    if isinstance(target_date_time, str):
        days_from_now = (date.today() - date.fromisoformat(target_date_time[:10])).days
    elif isinstance(target_date_time, datetime):
        days_from_now = (date.today() - target_date_time.date()).days
    elif isinstance(target_date_time, datetime.date):
        days_from_now = date.today() - target_date_time
    else:
        print("Not too sure about this date format.")
    if days_from_now < 90:
        # Some very recent events do not get much scramble room. So, let's pad that value:
        days_from_now = 90
    random_days = random_number_within_percent(target_number=days_from_now, percent=30, k=k)
    
    random_dates = []
    for dd in random_days:
        random_dates.append(common.make_date_pretty(date_time_string=(
            datetime.now() - timedelta(days=dd))))
    return random_dates

if __name__ == '__main__':
    """Will connect you to the database when you run questions.py interactively"""
    from server import app
    connect_to_db(app)
