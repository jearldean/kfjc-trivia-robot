"""Script to seed the trivia database."""

import os
from random import choice
import csv
import itertools
from datetime import datetime

from server import app
from model import db, connect_to_db
import common
import users
import questions
import user_answers
import playlists
import playlist_tracks
import albums
import tracks
import collection_tracks

DB_NAME = "trivia"

GAMEPLAY_DATA_PATH = 'test_data/test_data.json'
NUM_SEED_ANSWERS = 10

PLAYLIST_DATA_PATH = 'station_data/playlist.csv'
PLAYLIST_TRACK_DATA_PATH = 'station_data/playlist_track.csv'
ALBUM_DATA_PATH = 'station_data/album.csv'
TRACK_DATA_PATH = 'station_data/track.csv'
COLLECTION_TRACK_DATA_PATH = 'station_data/coll_track.csv'
CHUNK_SIZE = 100000


def seed_db():
    start1 = common.time_stamp()
    setup_seed_db()
    seed_gameplay_tables()
    seed_station_data_tables()
    common.timer(start1, operation="Seed Database")

def setup_seed_db():
    # Change this before going to production; 
    # we won't want to dump our user data everytime we import fresh station data.

    # Purge old databases:
    os.system(f"dropdb {DB_NAME}")
    os.system(f"createdb {DB_NAME}")

    connect_to_db(app)
    db.create_all()

def seed_gameplay_tables():
    start2 = common.time_stamp()
    test_data = common.open_json_files(GAMEPLAY_DATA_PATH)

    for one_user in test_data["users"]:
        a, b, c, d = one_user  # unpack
        users.create_user(email=a, fname=b, password=c, salt=d)

    for one_question in test_data["questions"]:
        a, b = one_question  # unpack
        questions.create_question(question=a, acceptable_answers=b)
        
    # possible_answers is just a testing device:
    possible_answers = questions.compile_possible_answers() + [""]  # Plus a chance to SKIP question

    for _ in range(NUM_SEED_ANSWERS):
        for user_instance in users.get_users():
            user_answers.create_user_answer(
                user_instance=user_instance,
                question_instance=questions.get_random_question(), 
                answer_given=choice(possible_answers))
                    
    db.session.commit()
    common.timer(start2, operation="Seed Gameplay Tables")

def seed_station_data_tables():
    table_tuples = [
        (PLAYLIST_DATA_PATH, create_playlists),
        (PLAYLIST_TRACK_DATA_PATH, create_playlist_tracks),
        (ALBUM_DATA_PATH, create_albums),
        (TRACK_DATA_PATH, create_tracks),
        (COLLECTION_TRACK_DATA_PATH, create_collection_tracks)]

    for each_table in table_tuples:
        seed_a_large_csv(each_table[0], each_table[1])

def seed_a_large_csv(file_path, row_handler):
    start_time = common.time_stamp()
    num_loops = how_many_loops_needed_for_large_csv(file_path)

    for i in range(num_loops):
        print(f"\n\nNow attempting {file_path}, Loop {i+1}:")
        start_mark, end_mark = get_start_and_end_marks(loop_number=i)

        with open(file_path, 'r') as file:
            reader = csv.reader(file)

            for row in itertools.islice(reader, start_mark, end_mark):
                row_handler(row)
        
        db.session.commit()
    
    common.timer(start_time, operation=f"{file_path} import")

def create_playlists(row):
    playlist_id = int(row[0])
    user_id = int(row[1])
    air_name = row[2].strip()
    start_time = cell_value_may_be_null(row[3])
    end_time = cell_value_may_be_null(row[4])
    playlists.create_playlist(playlist_id=playlist_id, user_id=user_id, air_name=air_name,
        start_time=start_time, end_time=end_time)

def create_playlist_tracks(row):
    playlist_id = int(row[0])
    indx = cell_value_may_be_null(row[1])
    is_current = cell_value_may_be_null(row[2])
    artist = title_fixer(row[3])
    track_title = title_fixer(row[4])
    album_title = title_fixer(row[5])
    album_id = cell_value_may_be_null(row[6])
    album_label = title_fixer(row[7])
    time_played = cell_value_may_be_null(row[8])  # '2022-01-19 22:04:31'
    playlist_tracks.create_playlist_track(playlist_id=playlist_id, indx=indx, 
        is_current=is_current, artist=artist, track_title=track_title, 
        album_title=album_title, album_id=album_id, album_label=album_label,
        time_played=time_played)

def create_albums(row):
    album_id = int(row[0])
    artist = title_fixer(row[1])
    title = title_fixer(row[2])
    is_collection = int(row[7])
    albums.create_album(album_id=album_id, artist=artist, title=title, is_collection=is_collection)

def create_tracks(row):
    album_id = int(row[0])
    title = title_fixer(row[1])
    indx = cell_value_may_be_null(row[2])
    clean = int(row[3])
    tracks.create_track(album_id=album_id, title=title, indx=indx, clean=clean)

def create_collection_tracks(row):
    album_id = int(row[0])
    title = title_fixer(row[1])
    artist = title_fixer(row[2])
    indx = cell_value_may_be_null(row[3])
    clean = int(row[4])
    collection_tracks.create_collection_track(album_id=album_id, title=title,
        artist=artist, indx=indx, clean=clean)

def title_fixer(a_string):
    """Fixes radio-station-naming-convention titles to English Readable titles."""
    a_string = a_string.replace("[coll]:", "")
    if ", the" in a_string.lower():
        without_the = a_string.replace(", the", "").replace(", The", "")
        return f"The {without_the}".strip()
    elif "," in a_string:

        # "Connick, Harry Jr."
        if " Jr." in a_string:
            a_string = a_string.replace(" Jr.", "")
            parts = a_string.split(",")
            new_string = " ".join(parts[1:]) + " " + parts[0]
            return new_string.strip() + " Jr."

        parts = a_string.split(",")
        # Incase there are 2 commas:
        new_string = " ".join(parts[1:]) + " " + parts[0]
        return new_string.strip()

    return a_string.strip()

def cell_value_may_be_null(cell_contents):
    """May be NULL or empty string."""
    if cell_contents in ['NULL', '', "0000-00-00 00:00:00"]:
        # psycopg2.errors.DatetimeFieldOverflow: date/time field value out of range: "0000-00-00 00:00:00"
        # https://stackoverflow.com/questions/33344587/insert-0000-00-00-000000-datetime-from-mysql-to-postgresql
        return None
    elif isinstance(cell_contents, int):
        return int(cell_contents)
    elif isinstance(cell_contents, datetime):
        return datetime.fromisoformat(cell_contents)
    else:
        # Maybe it's a string already. I'm tired of this.
        return str(cell_contents)

def how_many_lines(file_path):
    num_lines = sum(1 for line in open(file_path))
    print(f"{file_path} contains {num_lines:,} lines.")
    return num_lines

def how_many_loops_needed_for_large_csv(file_path):
    total_lines = how_many_lines(file_path)
    num_loops = int(total_lines / CHUNK_SIZE) + 1
    print(f"It will take {num_loops} loops in {CHUNK_SIZE:,} line chunks.")
    return num_loops

def get_start_and_end_marks(loop_number):
    if loop_number == 0:
        start_mark = 1
    else:
        start_mark = (loop_number * CHUNK_SIZE) + 1   # 1,      200001
    end_mark = (loop_number + 1) * CHUNK_SIZE         # 200000, 400000
    return start_mark, end_mark

if __name__ == "__main__":    
    connect_to_db(app)
    seed_db()
