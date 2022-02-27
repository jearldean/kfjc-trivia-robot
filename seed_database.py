"""Script to import station data and seed the question table."""

import os
import time
from server import app
from model import db, connect_to_db

import import_station_data as kfjc
import questions

DB_NAME = "trivia"

def recreate_all_tables():
    """Dump all data and re-create tables and relationships."""
    os.system(f"dropdb {DB_NAME}")
    os.system(f"createdb {DB_NAME}")

    connect_to_db(app)
    db.create_all()
    

def nuclear_option():
    tic = time.perf_counter()
    recreate_all_tables()  # I DELETE DATA!
    kfjc.import_all_tables()
    toc = time.perf_counter()
    mins = float((toc - tic)/60)
    print(f"Importing Station Data took {mins:0.4f} minutes.")
    tic = time.perf_counter()
    questions.make_all_the_questions()
    toc = time.perf_counter()
    mins = float((toc - tic)/60)
    print(f"Seeding Questions took {mins:0.4f} minutes.")

if __name__ == "__main__":    
    connect_to_db(app)
