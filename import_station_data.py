"""Import Station Data from csvs."""

import csv
import itertools
from sqlalchemy import create_engine

from server import app
from model import db, connect_to_db, Playlist, PlaylistTrack, Album, Track
import playlists
import playlist_tracks
import albums
import tracks

import common

DB_NAME = "trivia"

PLAYLIST_DATA_PATH = 'station_data/playlist.csv'
PLAYLIST_TRACK_DATA_PATH = 'station_data/playlist_track.csv'
ALBUM_DATA_PATH = 'station_data/album.csv'
TRACK_DATA_PATH = 'station_data/track.csv'
COLLECTION_TRACK_DATA_PATH = 'station_data/coll_track.csv'
CHUNK_SIZE = 100000  # lines

def drop_and_create_station_tables():
    """Drop and Create new station tables.  Don't drop the whole DB."""

    engine = create_engine(f"postgresql:///{DB_NAME}")

    for table in [Playlist, PlaylistTrack, Album, Track]:
        table.__table__.drop(engine)
        table.__table__.create(engine)

def import_all_tables():
    """ """
    data_path_and_function = [
        (PLAYLIST_DATA_PATH, create_playlists),
        (PLAYLIST_TRACK_DATA_PATH, create_playlist_tracks),
        (ALBUM_DATA_PATH, create_albums),
        (COLLECTION_TRACK_DATA_PATH, seed_collection_tracks),
        (TRACK_DATA_PATH, create_tracks)]

    for each_tuple in data_path_and_function:
        file_path, row_handler = each_tuple  # unpack
        seed_a_large_csv(file_path=file_path, row_handler=row_handler)

def seed_a_large_csv(file_path, row_handler):
    """Large files must be broken into chunks."""

    num_loops = get_num_loops(file_path=file_path)

    for i in range(num_loops):
        print(f"\n\nNow attempting {file_path}, Loop {i+1}:")
        start_mark, end_mark = get_start_chunk_and_end_chunk_row_indexes(
            loop_number=i)

        with open(file_path, 'r') as file:
            reader = csv.reader(file)

            for row in itertools.islice(reader, start_mark, end_mark):
                row_handler(row)  # This points to each table's import function.
        
        db.session.commit()  # Commit after each large chunk.

def get_num_loops(file_path):
    """Get the number of loops it will take to import a CSV file for a given CHUNK_SIZE."""

    num_lines = sum(1 for _ in open(file_path))
    num_loops = int(num_lines / CHUNK_SIZE) + 1
    print(f"It will take {num_loops} loops in {CHUNK_SIZE:,} line chunks.")
    return num_loops

def get_start_chunk_and_end_chunk_row_indexes(loop_number):
    """Identify the start and end rows for a data chunk to be imported."""

    if loop_number == 0:
        return 1, CHUNK_SIZE
    else:
        return loop_number * CHUNK_SIZE, (loop_number + 1) * CHUNK_SIZE

def create_playlists(row):
    """Add all playlists rows."""

    fixed_start_time, fixed_end_time = common.fix_playlist_times(
        start_time=row[3], end_time=row[4])

    playlists.create_playlist(
        kfjc_playlist_id=common.coerce_imported_data(row[0]),
        dj_id=common.coerce_imported_data(row[1]),
        air_name=common.coerce_imported_data(row[2]),
        start_time=common.coerce_imported_data(fixed_start_time),
        end_time=common.coerce_imported_data(fixed_end_time))

def create_playlist_tracks(row):
    """Add all playlist_tracks rows."""

    album_title = common.coerce_imported_data(row[5])
    artist = common.coerce_imported_data(row[3])
    track_title = common.coerce_imported_data(row[4])

    if all(v is None for v in [album_title, artist, track_title]):
        # Not importing blank rows reduced the table size by
        # 282,167 rows (11%) and reduced import time by 50s:
        return  

    playlist_tracks.create_playlist_track(
        kfjc_playlist_id=common.coerce_imported_data(row[0]),
        indx=common.coerce_imported_data(row[1]), 
        kfjc_album_id=common.coerce_imported_data(row[6]),
        album_title=album_title,
        artist=artist,
        track_title=track_title,
        time_played=common.coerce_imported_data(row[8]))
    
def create_albums(row):
    """Add all albums rows."""

    albums.create_album(
        kfjc_album_id=common.coerce_imported_data(row[0]),
        artist=common.coerce_imported_data(row[1]),
        title=common.coerce_imported_data(row[2]))

def seed_collection_tracks(row):
    """Add all collection tracks rows."""
    
    tracks.create_track(
        kfjc_album_id=common.coerce_imported_data(row[0]),
        artist=common.coerce_imported_data(row[2]),
        title=common.coerce_imported_data(row[1]),
        indx=common.coerce_imported_data(row[3]))

def create_tracks(row):
    """Add all tracks rows. These require artist lookup in the Albums table."""

    kfjc_album_id = common.coerce_imported_data(row[0])
    try:
        artist = albums.get_albums_by_kfjc_album_id(kfjc_album_id).artist
    except AttributeError:
        artist = None

    tracks.create_track(
        kfjc_album_id=kfjc_album_id,
        artist=artist,
        title=common.coerce_imported_data(row[1]),
        indx=common.coerce_imported_data(row[3]))



if __name__ == "__main__":    
    connect_to_db(app)
