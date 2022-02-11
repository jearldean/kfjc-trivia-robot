"""Question operations for KFJC Trivia Robot."""

import datetime
from sqlalchemy.sql.expression import func, distinct

from model import db, connect_to_db, Playlist, PlaylistTrack, Album, Track
import common
import questions
import playlists

DJ_MINIMUM_SHOWS = 20  # So that obscure and impossible to guess DJs don't show up in the survey.

def make_questions():

    parameterized_questions = [
        {
            "question": "How many KFJC DJs are there?",
            "question_type": "number",
            "calculate_answer": common.get_count(Playlist.dj_id),
            "rephrase_the_question": "There are this many KFJC DJs!"},
        {
            "question": "Since we started counting, how many shows have there been?",
            "question_type": "number",
            "calculate_answer": common.get_count(Playlist.id_),
            "rephrase_the_question": "There are this many shows in our records:"},
        {
            "question": "Since we started counting, how many songs have been played on KFJC?",
            "question_type": "number",
            "calculate_answer": common.get_count(PlaylistTrack.id_),
            "rephrase_the_question": "We've played this many songs since we began keeping track!"},
        {
            "question": "How many albums are in the KFJC Library?",
            "question_type": "number",
            "calculate_answer": common.get_count(Album.id_),
            "rephrase_the_question": "There are this many albums in our library:"},
        {
            "question": "How many artists are in the KFJC Library?",
            "question_type": "number",
            "calculate_answer": common.get_count(Album.artist),
            "rephrase_the_question": "There are this many artists in our library:"},
        {
            "question": "How many tracks are there in the KFJC Library?",
            "question_type": "number",
            "calculate_answer": common.get_count(Track.id_),
            "rephrase_the_question": "There are this many tracks in our library:"},
        {
            "question": "If a track is about 4 minutes long, how long would it take to listen to all tracks are in the KFJC Library?",
            "question_type": "duration",
            "calculate_answer": 4 * common.get_count(Track.id_),
            "rephrase_the_question": "It would take this long to listen to all the tracks in the KFJC Library!"},
        {
            "question": "When did KFJC begin collecting this data?",
            "question_type": "date",
            "calculate_answer": db.session.query(func.min(Playlist.start_time)).first()[0],
            "rephrase_the_question": "We began collecting this data on:"},
        {
            "question": "Just how fresh is this data?",
            "question_type": "date",
            "calculate_answer": db.session.query(func.max(Playlist.start_time)).first()[0],
            "rephrase_the_question": "The last data scrape for this page was on:"}
    ]

    for pq in parameterized_questions:
        if pq["question_type"] == "number":
            display_answer = f'{pq["calculate_answer"]:,}'
            calculate_answer = pq["calculate_answer"]
        elif pq["question_type"] == "date":
            calculate_answer = pq["calculate_answer"].isoformat()
            display_answer = common.make_date_pretty(pq["calculate_answer"])
        elif pq["question_type"] == "duration":
            calculate_answer = pq["calculate_answer"]
            display_answer = common.minutes_to_years(pq["calculate_answer"])
        else:  # No handler, do your best:
            calculate_answer = pq["calculate_answer"]
            display_answer = pq["calculate_answer"]

        questions.create_question(
            question=pq["question"],
            question_type=pq["question_type"],
            acceptable_answers={
                "calculate_answer": calculate_answer,
                "display_answer": display_answer,
                "rephrase_the_question": pq["rephrase_the_question"]})

    db.session.commit()


def dj_popularity_questions():
    """{
    'Brian Damage': {
        'dj_id': 443, 
        'shows': 1, 
        'first_show': datetime.datetime(2021, 12, 1, 2, 0, 49), 
        'last_show': datetime.datetime(2021, 12, 1, 2, 0, 49), 
        'playlist_ids': [66050]}
    """
    dj_popularity_dict_shows = {}
    dj_popularity_dict_first_show = {}
    dj_popularity_dict = {}
    unique_dj_ids, _ = playlists.get_all_dj_ids()
    for dj_id in unique_dj_ids:
        air_name, count_playlists, first_show, last_show, their_playlists = (
            playlists.get_all_playlists_by_dj_id(dj_id=dj_id))
        playlist_ids = [playlist.kfjc_playlist_id for playlist in their_playlists]
        if count_playlists > DJ_MINIMUM_SHOWS and air_name and "KFJC" not in air_name:
            dj_popularity_dict_shows[air_name] = count_playlists
            dj_popularity_dict_first_show[air_name] = int(first_show.timestamp())
            dj_popularity_dict[air_name] = {
                "dj_id": dj_id,
                "shows": count_playlists,
                "first_show": first_show,
                "last_show": last_show,
                "playlist_ids": playlist_ids}

    #print(common.print_a_popularity_dict_in_order(dj_popularity_dict_shows)) 
    #print(common.print_a_popularity_dict_in_order(dj_popularity_dict_first_show, high_to_low=False))

    #print(dj_popularity_dict['Robert Emmett'])
    #print(dj_popularity_dict["Spliff Skankin'"])

    """
    Where is Robert Emmett (62)? Where is splif skankin (177)?
    most_shows = max(int(d["shows"]) for d in dj_popularity_dict.values())
    first_on_air = min(int(d["first_show"]) for d in dj_popularity_dict.values())
    print(most_shows)
    print(first_on_air)"""


if __name__ == '__main__':
    """Will connect you to the database when you run questions.py interactively"""
    from server import app
    connect_to_db(app)
