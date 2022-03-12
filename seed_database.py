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
    """Import and fix all Station Data and Seed All Questions."""
    recreate_all_tables()  # I DELETE DATA!

    tic = time.perf_counter()
    kfjc.import_all_tables()
    toc = time.perf_counter()
    questions.make_all_questions()
    hours = float((toc - tic)/3600)
    print(f"Importing Station Data took {hours:0.4f} hours.")


if __name__ == "__main__":
    connect_to_db(app)
