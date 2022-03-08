"""Question operations for KFJC Trivia Robot."""

from datetime import datetime, timedelta, date
import time
from operator import attrgetter
from random import randrange, choice, choices, shuffle
from typing import List, Any, NamedTuple

from model import Album, db, connect_to_db, Answer, PlaylistTrack, Question
import djs
import tracks
import albums
import playlists
import playlist_tracks
import tracks
import common

SEED_QUESTION_COUNT = 30
QUESTION_TYPES = {
    'djs': "A Question about DJs:",
    'artists': "A Question about Artists:",
    'albums': "A Question about Albums:",
    'tracks': "A Question about Tracks:"}


def create_question(
        question_type: str, ask_question: str, present_answer: str,
        acceptable_answer: str, display_shuffled_answers: List[str],
        present_answer_data_headings: List[str],
        present_answer_data: List[Any]) -> Question:
    """Create and return a new question."""

    question = Question(
        question_type=question_type,
        ask_question=ask_question,
        present_answer=present_answer,
        acceptable_answer=acceptable_answer,
        display_shuffled_answers=display_shuffled_answers,
        present_answer_data_headings=present_answer_data_headings,
        present_answer_data=present_answer_data)

    db.session.add(question)
    # Don't forget to call model.db.session.commit() when done adding items.

    return question


def get_question_by_id(question_id: int) -> Question:
    """Return a question by question_id."""

    return Question.query.get(question_id)

# -=-=-=-=-=-=-=-=-=-=-=- Choose Random Question -=-=-=-=-=-=-=-=-=-=-=-


def get_unique_question(user_id: int) -> Question:
    """Pose a question to the user that they have not answered before."""

    users_answers = Answer.query.filter(Answer.user_id == user_id).all()
    user_already_answered = [
        users_answer.question_id for users_answer in users_answers]
    question_ids = [
        one_question.question_id for one_question in Question.query.all()]
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
    create_dj_favorites_questions()
    create_top_ten_questions()
    albums_by_an_artist()
    artist_of_an_album()
    tracks_on_an_album()
    create_last_play_questions()
    toc = time.perf_counter()
    mins = float((toc - tic)/60)
    print(
        f"Seeding Questions took {mins:0.4f} minutes "
        "using SEED_QUESTION_COUNT={SEED_QUESTION_COUNT}.")

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def who_is_the_oldest_dj():
    """Create questions where the oldest DJ is the answer."""
    reverse_display_answers = False
    results_named_tuple = playlists.get_djs_by_first_show(
        reverse=reverse_display_answers)
    ask_questions = [
        "From these choices, who graduated Radio 90A (DJ Training) first?",
        "Out of these four, who has been a KFJC DJ the longest?",
        "Who finished Radio 90A (DJ Training) before any of the "
        "other choices?"]
    present_answers = [
        "This person was on the air first:",
        "This person hit the airwaves first:",
        "This DJ was first on the air:"]
    search_key = 'firstshow'
    present_answer_data_headings = ["Air Name", "First Show"]
    dj_competition_engine(
        reverse_display_answers=reverse_display_answers,
        results_named_tuple=results_named_tuple,
        ask_questions=ask_questions, present_answers=present_answers,
        present_answer_data_headings=present_answer_data_headings,
        search_key=search_key)


def who_is_the_newest_dj():
    """Create questions where the newest DJ is the answer."""
    reverse_display_answers = True
    results_named_tuple = playlists.get_djs_by_first_show(
        reverse=reverse_display_answers)
    ask_questions = [
        "From these choices, who graduated Radio 90A (DJ Training) last?",
        "Spot the greenhorn! From these choices, who is the most recent "
        "grad of Radio 90A (DJ Training)?",
        "Pick the rookie! Who is the newest DJ out of these four?"]
    present_answers = [
        "This person is the most recent DJ:",
        "This person is newest to our airwaves:",
        "Here's the newest DJ from that lot:", "Our newest DJ is:"]
    present_answer_data_headings = ["Air Name", "First Show"]
    search_key = 'firstshow'
    dj_competition_engine(
        reverse_display_answers=reverse_display_answers,
        results_named_tuple=results_named_tuple,
        ask_questions=ask_questions, present_answers=present_answers,
        present_answer_data_headings=present_answer_data_headings,
        search_key=search_key)


def who_has_the_most_shows():
    """Create questions where the DJ with the most shows is the answer."""
    reverse_display_answers = True
    results_named_tuple = playlists.get_djs_by_show_count()
    ask_questions = [
        "From these choices, which KFJC DJ has the most shows?",
        "Out of these four, who has done the most shows?",
        "Which of these four DJs has done the most shows?"]
    present_answers = [
        "This person has done the more than the others:",
        "This person has more shows:", "This DJ has more shows:"]
    present_answer_data_headings = ["Air Name", "Show Count"]
    search_key = 'showcount'
    dj_competition_engine(
        reverse_display_answers=reverse_display_answers,
        results_named_tuple=results_named_tuple,
        ask_questions=ask_questions, present_answers=present_answers,
        present_answer_data_headings=present_answer_data_headings,
        search_key=search_key)


def dj_competition_engine(
        results_named_tuple: NamedTuple, ask_questions: List[str],
        present_answers: List[str], reverse_display_answers: bool,
        present_answer_data_headings: List[str], search_key: str):
    """Create DJ Comparison Questions."""
    winner_slice = results_named_tuple[:SEED_QUESTION_COUNT]  # Top 30
    loser_slice = results_named_tuple[SEED_QUESTION_COUNT:]  # Everyone Else
    for the_right_answer in winner_slice:
        three_wrong_answers = choices(loser_slice, k=3)
        answer_pile = [the_right_answer] + three_wrong_answers
        present_answer_data = []
        display_shuffled_answers = []

        for zz in sorted(
                answer_pile, key=attrgetter(search_key),
                reverse=reverse_display_answers):
            if "Show Count" in present_answer_data_headings:  # Count Question
                item_value = common.format_an_int_with_commas(
                    your_int=zz.showcount)
            elif "First Show" in present_answer_data_headings:
                item_value = common.make_date_pretty(
                    date_time_string=zz.firstshow)
            else:  # Last Show
                item_value = common.make_date_pretty(
                    date_time_string=zz.lastshow)
            air_name = djs.get_airname_for_dj(dj_id=zz.dj_id)
            present_answer_data.append([air_name, item_value])
            display_shuffled_answers.append(air_name)

        acceptable_answer = display_shuffled_answers[0]
        shuffle(display_shuffled_answers)
        create_question(
            question_type=QUESTION_TYPES['djs'],
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answer=acceptable_answer,
            display_shuffled_answers=display_shuffled_answers,
            present_answer_data_headings=present_answer_data_headings,
            present_answer_data=present_answer_data)

    db.session.commit()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def when_was_dj_last_on_the_air():
    """Create questions where the date of a DJ's last show is the answer."""
    results_named_tuple = playlists.get_djs_by_last_show(reverse=False)
    random_last_shows = choices(results_named_tuple, k=SEED_QUESTION_COUNT)
    for last_show in random_last_shows:
        the_right_answer = last_show.lastshow  # A Datetime Object.
        three_wrong_answers = random_date_surrounding_another_date(
            the_right_answer, k=3)
        the_pretty_right_answer = common.make_date_pretty(
            date_time_string=the_right_answer)
        answer_pile = [the_pretty_right_answer] + three_wrong_answers
        dj_id = last_show.dj_id
        air_name = djs.get_airname_for_dj(dj_id=dj_id, posessive=False)
        air_name_posessive = djs.get_airname_for_dj(
            dj_id=dj_id, posessive=True)
        ask_questions = [
            f"Can you guess {air_name_posessive} most recent show?",
            f"When was {air_name} last on the air?",
            f"When was {air_name_posessive} last show?"]
        present_answers = [
            f"{air_name} was last on the air:",
            f"This is when {air_name} last did a show:",
            f"This is the last time we heard {air_name} on the air:"]
        present_answer_data = [[the_pretty_right_answer, ""]]  # Only one row.
        shuffle(answer_pile)
        create_question(
            question_type=QUESTION_TYPES['djs'],
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answer=the_pretty_right_answer,
            display_shuffled_answers=answer_pile,
            # No headings. Just a one-sentence answer:
            present_answer_data_headings=["", ""],
            present_answer_data=present_answer_data)

    db.session.commit()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def create_dj_favorites_questions():
    """Create questions about top plays of an Artist/Album/Track by a DJ."""
    dj_favorites_engine(media='track')
    dj_favorites_engine(media='artist')
    dj_favorites_engine(media='album')


def dj_favorites_engine(media: str):
    """Create questions where a DJ's most played media is the answer."""
    dj_id_pool = playlists.get_all_dj_ids()
    x_random_dj_ids = choices(dj_id_pool, k=SEED_QUESTION_COUNT)
    for dj_id in x_random_dj_ids:
        if media == 'artist':
            answer_key = playlist_tracks.get_favorite_artists(
                dj_id=dj_id, reverse=True, min_plays=5)
        elif media == 'album':
            answer_key = playlist_tracks.get_favorite_albums(
                dj_id=dj_id, reverse=True, min_plays=5)
        else:  # 'track'
            answer_key = playlist_tracks.get_favorite_tracks(
                dj_id=dj_id, reverse=True, min_plays=5)
        if len(answer_key) < 10:
            # Some Djs are so new they don't have a body of work
            # large enough to produce favorites scores:
            continue
        air_name = djs.get_airname_for_dj(dj_id=dj_id)
        air_name_posessive = djs.get_airname_for_dj(
            dj_id=dj_id, posessive=True)
        dj_favorites = answer_key[:5]
        less_favorite = answer_key[5:]
        for the_right_answer in dj_favorites:
            ask_questions = [
                f"From these choices, which {media} does {air_name} "
                f"like most?",
                f"Which {media} is {air_name_posessive} favorite out "
                f"of these four?",
                f"From these four choices, which {media} has DJ "
                f"{air_name} played the most?"]
            present_answers = [
                f"{air_name} likes this {media} the most:",
                f"{air_name} has played this {media} the most:",
                f"This {media} is played by DJ {air_name} a lot:"]
            three_wrong_answers = choices(less_favorite, k=3)
            answer_pile = [the_right_answer] + three_wrong_answers
            present_answer_data = []
            display_shuffled_answers = []
            for zz in sorted(
                    answer_pile, key=attrgetter('plays'), reverse=True):
                if media == 'artist':
                    present_answer_data.append([zz.artist, zz.plays])
                    display_shuffled_answers.append(zz.artist)
                    acceptable_answer = the_right_answer.artist
                elif media == 'album':
                    present_answer_data.append([zz.album_title, zz.plays])
                    display_shuffled_answers.append(zz.album_title)
                    acceptable_answer = the_right_answer.album_title
                else:  # 'track'
                    present_answer_data.append([zz.track_title, zz.plays])
                    display_shuffled_answers.append(zz.track_title)
                    acceptable_answer = the_right_answer.track_title
            shuffle(display_shuffled_answers)
            create_question(
                question_type=QUESTION_TYPES[media+'s'],
                ask_question=choice(ask_questions),
                present_answer=choice(present_answers),
                acceptable_answer=acceptable_answer,
                display_shuffled_answers=display_shuffled_answers,
                present_answer_data_headings=[media.title(), "Plays"],
                present_answer_data=present_answer_data)

    db.session.commit()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def create_top_ten_questions():
    """Create questions about an Artist/Album/Track in the KFJC Top10."""
    top_ten_engine(media='track')
    top_ten_engine(media='artist')
    top_ten_engine(media='album')


def top_ten_engine(media: str):
    """Create questions where top-played media is the answer."""
    old, _ = common.get_ages(PlaylistTrack.time_played)
    # I improved this to go back to 1995-09-19.
    days_to_choose_from = (datetime.now() - old).days
    random_days_before_today = choices(
        range(days_to_choose_from), k=SEED_QUESTION_COUNT)
    for random_days in random_days_before_today:
        start_date = date.today() - timedelta(days=random_days)
        # During a Week:
        end_date = date.today() - timedelta(days=(random_days - 7))
        pretty_date = common.make_date_pretty(start_date)

        ask_questions = [
            f"All of these {media}s were in the KFJC Top40 during "
            f"the week of {pretty_date} but which one made the Top10?",
            f"All four {media}s were in the KFJC Top40 during the week "
            f"of {pretty_date} but which was in the Top10?",
            f"All these {media}s were in the KFJC Top40 during the week "
            f"of {pretty_date}. Which {media} was in the Top10?"]
        present_answers = [
            f"Here are the KFJC Top40 {media}s during the week of "
            f"{pretty_date}:",
            f"These were the KFJC Top40 {media}s on {pretty_date}:",
            f"During the week of {pretty_date}, this is the KFJC "
            f"Top40 by {media}:"]

        if media == 'artist':
            answer_key = playlist_tracks.get_top10_artists(
                start_date, end_date, n=40)
        elif media == 'album':
            answer_key = playlist_tracks.get_top10_albums(
                start_date, end_date, n=40)
        else:  # 'track'
            answer_key = playlist_tracks.get_top10_tracks(
                start_date, end_date, n=40)
        if len(answer_key) == 0:
            continue  # Dud list.

        winners = answer_key[:10]  # Top Ten
        one_winner = choice(winners)
        losers = answer_key[10:]  # Bottom 30
        three_wrong_answers = choices(losers, k=3)
        answer_pile = [one_winner] + three_wrong_answers
        present_answer_data = []
        display_shuffled_answers = []

        for zz in sorted(answer_pile, key=attrgetter('plays'), reverse=True):
            if media == 'artist':
                display_shuffled_answers.append(zz.artist)
            elif media == 'album':
                display_shuffled_answers.append(zz.album_title)
            else:  # 'track'
                display_shuffled_answers.append(zz.track_title)
        acceptable_answer = display_shuffled_answers[0]
        shuffle(display_shuffled_answers)

        # The answer displayed will be the entire KFJC Top40:
        for zz in sorted(answer_key, key=attrgetter('plays'), reverse=True):
            if media == 'artist':
                present_answer_data.append([zz.artist, zz.plays])
            elif media == 'album':
                present_answer_data.append([zz.album_title, zz.plays])
            else:  # 'track'
                present_answer_data.append([zz.track_title, zz.plays])

        create_question(
            question_type=QUESTION_TYPES[media+'s'],
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answer=acceptable_answer,
            display_shuffled_answers=display_shuffled_answers,
            present_answer_data_headings=[media.title(), "Plays"],
            present_answer_data=present_answer_data)

    db.session.commit()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def get_four_random_albums() -> List[Album]:
    """Four random album objects for question creation."""
    four_random_albums = []
    for _ in range(4):
        # Get 4 random albums:
        random_kfjc_album_id = playlist_tracks.get_a_random_kfjc_album_id()
        random_album = albums.get_album_by_id(
            kfjc_album_id=random_kfjc_album_id)
        four_random_albums.append(random_album)
    return four_random_albums


def albums_by_an_artist():
    """Formulate a question about albums by an artist."""
    question_type = "A Question about an Album:"
    for _ in range(SEED_QUESTION_COUNT):
        four_random_albums = get_four_random_albums()
        # The first album shall be the winner:
        winner_artist = four_random_albums[0].artist
        winner_album_title = four_random_albums[0].title
        ask_questions = [
            f"Which album is by the artist '{winner_artist}'?",
            f"Can you pick the album that's from the artist "
            f"'{winner_artist}'?",
            f"Which album did the artist '{winner_artist}' make?"]
        present_answers = [
            f"This album is from '{winner_artist}':",
            f"This album is by '{winner_artist}':",
            f"'{winner_artist}' made this album:"]

        album_titles = [album.title for album in four_random_albums]
        shuffle(album_titles)
        present_answer_data = [
            [album.artist, album.title] for album in four_random_albums]
        if present_answer_data:  # Null Spike Jones title made it in there.
            create_question(
                question_type=question_type,
                ask_question=choice(ask_questions),
                present_answer=choice(present_answers),
                acceptable_answer=winner_album_title,
                display_shuffled_answers=album_titles,
                present_answer_data_headings=["Artist", "Album"],
                present_answer_data=present_answer_data)

    db.session.commit()


def artist_of_an_album():
    """Formulate a question about artist of an album."""
    for _ in range(SEED_QUESTION_COUNT):
        four_random_albums = get_four_random_albums()
        # The first album shall be the winner:
        winner_artist = four_random_albums[0].artist
        winner_album_title = four_random_albums[0].title
        ask_questions = [
            f"Which artist made the album '{winner_album_title}'?",
            f"Can you pick the artist who made the album "
            f"'{winner_album_title}'?",
            f"Name the artist of the album '{winner_album_title}'?"]
        present_answers = [
            f"This artist made '{winner_album_title}':",
            f"This artist of '{winner_album_title}' is:"]

        album_artists = [album.artist for album in four_random_albums]
        shuffle(album_artists)
        present_answer_data = [
            [album.artist, album.title] for album in four_random_albums]
        if present_answer_data:
            create_question(
                question_type=QUESTION_TYPES['artists'],
                ask_question=choice(ask_questions),
                present_answer=choice(present_answers),
                acceptable_answer=winner_artist,
                display_shuffled_answers=album_artists,
                present_answer_data_headings=["Artist", "Album"],
                present_answer_data=present_answer_data)

    db.session.commit()


def get_any_track_title_from_this_album(kfjc_album_id: int) -> str:
    """Get one track title from an album."""
    track_objects = tracks.get_tracks_by_kfjc_album_id(
        kfjc_album_id=kfjc_album_id)
    one_random_track = choice(track_objects)
    return one_random_track.title


def get_all_track_titles_from_this_album(kfjc_album_id: int) -> List[str]:
    """Get titles for all tracks on an album by kfjc_album_id."""
    track_objects = tracks.get_tracks_by_kfjc_album_id(
        kfjc_album_id=kfjc_album_id)
    return [jj.title for jj in track_objects]


def tracks_on_an_album():
    """Formulate a question about tracks on an album."""
    question_type = "A Question about a Track:"
    for _ in range(SEED_QUESTION_COUNT):
        four_random_albums = get_four_random_albums()
        # The first album shall be the winner:
        winner_artist = four_random_albums[0].artist
        winner_album_title = four_random_albums[0].title
        winner_track_title = get_any_track_title_from_this_album(
            kfjc_album_id=four_random_albums[0].kfjc_album_id)
        present_answer_data = []
        for one_track_title in get_all_track_titles_from_this_album(
                kfjc_album_id=four_random_albums[0].kfjc_album_id):
            present_answer_data.append([winner_artist, one_track_title])
        artist_posessive = winner_artist + common.the_right_apostrophe(
            winner_artist)
        ask_questions = [
            f"Name a track from {artist_posessive} album "
            f"'{winner_album_title}':",
            f"Can you pick the track that's from {artist_posessive} "
            f"'{winner_album_title}' album?",
            f"Pick the track that's off {artist_posessive} album "
            f"'{winner_album_title}':"]
        present_answers = [
            f"Here is the track list for {artist_posessive} album "
            f"'{winner_album_title}':",
            f"These are the tracks on {artist_posessive} "
            f"'{winner_album_title}' album:",
            f"{artist_posessive} album '{winner_album_title}' "
            f"contains these tracks:"]

        answer_pile = [winner_track_title]
        for each_album in four_random_albums[1:]:  # Losers
            loser_track_title = get_any_track_title_from_this_album(
                kfjc_album_id=each_album.kfjc_album_id)
            answer_pile.append(loser_track_title)
        shuffle(answer_pile)

        create_question(
            question_type=question_type,
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answer=winner_track_title,
            display_shuffled_answers=answer_pile,
            present_answer_data_headings=["Artist", "Track"],
            present_answer_data=present_answer_data)

    db.session.commit()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def create_last_play_questions():
    """Create questions about the last time an
    Artist/Album/Track was played."""
    last_play_engine(media='track')
    last_play_engine(media='artist')
    last_play_engine(media='album')


def last_play_engine(media: str):
    """Create a question about the last time a media was played."""
    for _ in range(SEED_QUESTION_COUNT):
        if media == 'artist':
            random_media = playlist_tracks.get_a_random_artist()
        elif media == 'album':
            random_media = playlist_tracks.get_a_random_album()
        else:  # 'track'
            random_media = playlist_tracks.get_a_random_track()
        if not random_media:
            continue  # Dud list.
        ask_questions = [
            f"When was the last time we played the {media} "
            f"'{random_media}'?",
            f"When was the last time the {media} '{random_media}' "
            f"got any airplay?",
            f"When was the last time the {media} '{random_media}' "
            f"was played on KFJC?"]
        present_answers = [
            f"This is the last time we played the {media} "
            f"'{random_media}':",
            f"The last recorded play of the {media} '{random_media}'"
            f" on KFJC was:",
            f"The last time the {media} '{random_media}' was played was:"]
        # Search for apostrophe, must use double:
        random_media = random_media.replace("'", "''")
        if media == 'artist':
            answer_key = playlist_tracks.get_last_play_of_artist(
                random_media, reverse=True)
        elif media == 'album':
            answer_key = playlist_tracks.get_last_play_of_album(
                random_media, reverse=True)
        else:  # 'track'
            answer_key = playlist_tracks.get_last_play_of_track(
                random_media, reverse=True)

        if not answer_key:
            continue  # Dud list.
        winner = answer_key[0]  # First Hit

        the_right_answer = winner.time_played
        three_wrong_answers = random_date_surrounding_another_date(
            the_right_answer, k=3)
        the_pretty_right_answer = common.make_date_pretty(
            date_time_string=the_right_answer)
        answer_pile = [the_pretty_right_answer] + three_wrong_answers
        shuffle(answer_pile)
        present_answer_data = []
        for zz in answer_key:
            air_name = djs.get_airname_for_dj(dj_id=zz.dj_id)
            pretty_date = common.make_date_pretty(
                date_time_string=zz.time_played)
            if media == 'artist':
                media_title = zz.artist
            elif media == 'album':
                media_title = zz.album_title
            else:  # 'track'
                media_title = zz.track_title
            present_answer_data.append([
                f"{air_name} played the {media} '{media_title}' on ",
                pretty_date])

        create_question(
            question_type=QUESTION_TYPES[media+'s'],
            ask_question=choice(ask_questions),
            present_answer=choice(present_answers),
            acceptable_answer=the_pretty_right_answer,
            display_shuffled_answers=answer_pile,
            present_answer_data_headings=["Who played what", "Date"],
            present_answer_data=present_answer_data)

    db.session.commit()

# -=-=-=-=-=-=-=-=-=-=-=- Make Fake Answers -=-=-=-=-=-=-=-=-=-=-=-


def random_number_within_percent(
        target_number: int, percent: int = 40, k: int = 1) -> List[int]:
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


def random_date_surrounding_another_date(
        target_date_time: str, k: int = 1) -> List[str]:
    """Forget the time... just return a date."""

    if isinstance(target_date_time, str):
        days_from_now = (
            date.today() - date.fromisoformat(
                target_date_time[:10])).days
    elif isinstance(target_date_time, datetime):
        days_from_now = (date.today() - target_date_time.date()).days
    elif isinstance(target_date_time, datetime.date):
        days_from_now = date.today() - target_date_time
    else:
        print("Not too sure about this date format.")
    if days_from_now < 90:
        # Some very recent events do not get much scramble room.
        # So, let's pad that value:
        days_from_now = 90
    random_days = random_number_within_percent(
        target_number=days_from_now, percent=30, k=k)

    random_dates = []
    for dd in random_days:
        random_dates.append(common.make_date_pretty(date_time_string=(
            datetime.now() - timedelta(days=dd))))
    return random_dates


if __name__ == '__main__':
    """Will connect you to the database when you run
    questions.py interactively"""
    from server import app
    connect_to_db(app)
