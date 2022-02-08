"""Script to seed the trivia database."""

import os
import time
from server import app
from model import db, connect_to_db
#User, Question, Answer, Playlist, PlaylistTrack, Album, Track

import users
import import_station_data as kfjc
import questions
from random import choice

DB_NAME = "trivia"

PLAYLIST_DATA_PATH = 'station_data/playlist.csv'
PLAYLIST_TRACK_DATA_PATH = 'station_data/playlist_track.csv'
ALBUM_DATA_PATH = 'station_data/album.csv'
TRACK_DATA_PATH = 'station_data/track.csv'
COLLECTION_TRACK_DATA_PATH = 'station_data/coll_track.csv'
CHUNK_SIZE = 100000

NUM_SEED_USERS = 50
NUM_SEED_ANSWERS = 10

def recreate_all_tables():
    """Dump all data and re-create tables and relationships."""
    os.system(f"dropdb {DB_NAME}")
    os.system(f"createdb {DB_NAME}")

    connect_to_db(app)
    db.create_all()

def seed_fake_users():
    """Add all users rows."""

    fake_passwords = ["KFjC89.7", "TheWaVeoFThewESt",
        "yOUrS0urce4sOUnD", "RIP_CyToth_HearTEmoji"]

    for jj in range(NUM_SEED_USERS):
        users.create_user(
            username=f"fake_{jj}@aol.com",
            fname=f"Fake{jj}",
            password=choice(fake_passwords))

    db.session.commit() 

def seed_questions():
    questions.make_counts_questions()

def nuclear_option():
    tic = time.perf_counter()
    #recreate_all_tables()  ## I DELETE DATA!
    #kfjc.drop_and_create_station_tables()
    #kfjc.import_all_tables()
    #seed_fake_users()
    
    toc = time.perf_counter()
    print(f"Seed DB in {toc - tic:0.4f} seconds.")
    # Took an hour to unite tracks with artists through album IDs.

if __name__ == "__main__":    
    connect_to_db(app)
