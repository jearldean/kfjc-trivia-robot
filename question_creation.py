"""Question operations for KFJC Trivia Robot."""

import datetime
import random
from sqlalchemy.sql.expression import func, distinct, select

from operator import itemgetter

from model import db, connect_to_db, Playlist, PlaylistTrack, Album, Track
import common
import questions
import playlists

NUM_POP_Q = 20


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
    """195 DJs with 40+ shows."""

    dj_stats = playlists.dj_stats()

    dj_info_deck = {}
    for i in dj_stats:
        dj_info_deck[i[1]] = {
            'air_name': i[0], 
            'show_count': i[2], 
            'last_show': i[3], 
            'first_show': i[4]}

    dj_ids = list(dj_info_deck.keys())

    for _ in range(NUM_POP_Q):
        four_random_djs = random.choices(dj_ids, k=4)
        show_counts = [dj_info_deck[dj_id]['show_count'] for dj_id in four_random_djs]
        top_show_count = max(show_counts)

        winner = []
        losers = []
        display_all_answers = {}
        for dj_id in four_random_djs:
            dj_show_count = dj_info_deck[dj_id]['show_count']
            dj_air_name = dj_info_deck[dj_id]['air_name']
            if dj_show_count == top_show_count:
                winner.append(dj_air_name)
            else:
                losers.append(dj_air_name)
            display_all_answers[dj_show_count] = dj_air_name
            #display_all_answers.append(f"{dj_show_count} shows | {dj_info_deck[dj_id]['air_name']} ")
        sorted(display_all_answers.items())
        
        questions.create_question(
            question="Who has the most shows?",
            question_type="most_shows",
            acceptable_answers={
                "calculate_answer": winner[0],
                "display_answer": winner[0],
                "display_incorrect_answers": losers,
                "rephrase_the_question": "This DJ has the most shows:",
                "display_all_answers": display_all_answers})

    
    for _ in range(NUM_POP_Q):
        four_random_djs = random.choices(dj_ids, k=4)
        first_show = [dj_info_deck[dj_id]['first_show'] for dj_id in four_random_djs]
        earliest_show = min(first_show)

        winner = []
        losers = []
        display_all_answers = {}
        for dj_id in four_random_djs:
            #dj_first_show = common.make_date_pretty(dj_info_deck[dj_id]['first_show'].strftime('%Y-%m-%d %H:%M:%S'))
            dj_first_show = dj_info_deck[dj_id]['first_show'].strftime('%Y-%m-%d %H:%M:%S')
            dj_air_name = dj_info_deck[dj_id]['air_name']
            if dj_info_deck[dj_id]['first_show'] == earliest_show:
                winner.append(dj_air_name)
            else:
                losers.append(dj_air_name)
            display_all_answers[dj_first_show] = dj_air_name
            #display_all_answers.append(f"{dj_show_count} shows | {dj_info_deck[dj_id]['air_name']} ")
        sorted(display_all_answers.items())
        
        questions.create_question(
            question="Who was on the air first?",
            question_type="earliest_show",
            acceptable_answers={
                "calculate_answer": winner[0],
                "display_answer": winner[0],
                "display_incorrect_answers": losers,
                "rephrase_the_question": "This DJ was on the air first:",
                "display_all_answers": display_all_answers})

    db.session.commit()



if __name__ == '__main__':
    """Will connect you to the database when you run questions.py interactively"""
    from server import app
    connect_to_db(app)
