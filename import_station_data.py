"""Import Station Data from csv Files."""

import csv
import itertools
from random import choice
from datetime import datetime, timedelta

from server import app
from model import db, connect_to_db
import playlists
import playlist_tracks
import albums
import tracks

# -=-=-=-=-=-=-=-=-=-=-=- Clean up Data for Import -=-=-=-=-=-=-=-=-=-=-=-

BAD_TIMES = ["0000-00-00 00:00:00", "1970-01-01 01:00:00", "1969-12-31 16:00:00"]

def fix_playlist_times(start_time, end_time):
    """A few dates are borked but if the other time cell is populated,
    we can make a decent guess. Fixes 166 rows.
    
    >>> fix_playlist_times("1969-12-31 16:00:00", "1969-12-31 16:00:00")  # No change
    ('1969-12-31 16:00:00', '1969-12-31 16:00:00')
    >>> fix_playlist_times('2000-07-27 10:30:00', "1969-12-31 16:00:00")    # No change
    ('2000-07-27 10:30:00', '2000-07-27 13:30:00')
    >>> fix_playlist_times("1969-12-31 16:00:00", '2000-07-27 10:30:00')
    ('2000-07-27 07:30:00', '2000-07-27 10:30:00')
    """

    if start_time in BAD_TIMES and end_time not in BAD_TIMES:
        start_time = time_shift(end_time, shift=-3)
    elif end_time in BAD_TIMES and start_time not in BAD_TIMES:
        end_time = time_shift(start_time, shift=3)
    
    return start_time, end_time

def time_shift(one_datetime_cell, shift=3):
    """
    >>> time_shift('2000-07-27 10:30:00')
    '2000-07-27 13:30:00'
    >>> time_shift('2000-07-27 10:30:00', -3)
    '2000-07-27 07:30:00'
    """

    return (datetime.fromisoformat(one_datetime_cell) + 
        timedelta(hours=shift)).strftime('%Y-%m-%d %H:%M:%S')

def coerce_imported_data(one_cell):
    """Coerce incoming data to the correct type.
    >>> coerce_imported_data('NULL')
    >>> coerce_imported_data('Null')
    >>> coerce_imported_data("")
    >>> coerce_imported_data("0000-00-00 00:00:00")
    >>> coerce_imported_data("1969-12-31 16:00:00")
    >>> coerce_imported_data(-3)
    -3
    >>> coerce_imported_data(27)
    27
    >>> coerce_imported_data('Wave of the West, The ')
    'The Wave of the West'
    """

    if one_cell in [
        'NULL', "Null", '', " ", "?", ".", "..", "...", "*", "-", ",",
        "\""] + BAD_TIMES:
        return None
    elif isinstance(one_cell, int):
        return int(one_cell)
    elif isinstance(one_cell, datetime):
        return datetime.fromisoformat(one_cell)
    else:
        return fix_titles(some_title=one_cell)

def fix_titles(some_title):
    """Fixes radio-station-naming-convention titles to English Readable titles.
    
    >>> fix_titles("Connick, Harry Jr.")
    'Harry Connick Jr.'
    >>> fix_titles("Brown, James")
    'James Brown'
    """

    some_title = profanity_filter(title_string=some_title)

    if ", the" in some_title.lower():
        without_the = some_title.replace(", the", "").replace(", The", "")
        return f"The {without_the}".strip()
    elif "," in some_title:
        # "Connick, Harry Jr."
        if " Jr." in some_title:
            some_title = some_title.replace(" Jr.", "")
            parts = some_title.split(",")
            new_string = " ".join(parts[1:]) + " " + parts[0]
            return new_string.strip() + " Jr."

        parts = some_title.split(",")
        # Incase there are 2 commas:
        new_string = " ".join(parts[1:]) + " " + parts[0]
        return new_string.strip()

    return some_title

def profanity_filter(title_string):
    """
    Data comes from an edgey Radio station. Found out I needed a Profanity Filter.

    >>> profanity_filter(title_string="Pussy")
    'P&#128576;ssy'
    >>> profanity_filter(title_string="Shit")
    'Sh&#128169;t'
    """
    emojis = [
        "&#129296;", "&#129323;", "&#129325;",
        "&#129300;", "&#128526;", "&#128520;"]
    replace_with_emoji = choice(emojis)
    title_string = title_string.replace(
        "Fuck", f"F{replace_with_emoji}ck").replace(
        "Shit", f"Sh&#128169;t").replace(
        "Pussy", "P&#128576;ssy").replace(
        "[coll]:", "").replace(  # Station shorthand for collaboration tracks.
        "[Coll]:", "").replace(
        "  ", " ")

    return title_string.strip()

def add_missing_albums():
    """There are a handful of missing albums causing import failures."""
    missing_albums = [
        {"kfjc_album_id": 0, "artist": 'Various Artists', "title": 'Unknown Compilation', "is_collection": True},
        {"kfjc_album_id": 27, "artist": 'Pete & C.L. Smooth Rock', "title": 'Mecca and the Soul Bro', "is_collection": False},
        {"kfjc_album_id": 36, "artist": 'Sharon and the Dap King Jones', "title": 'What If We All Stopped', "is_collection": False},
        {"kfjc_album_id": 5050, "artist": 'Various Artists', "title": 'Unknown Compilation', "is_collection": True},
        {"kfjc_album_id": 269197, "artist": 'Al Larsen', "title": '\x01\t\x02', "is_collection": False},
        {"kfjc_album_id": 666070, "artist": 'The Gits', "title": 'Best Of: Music From and Inspired By The Film', "is_collection": False},
        {"kfjc_album_id": 684930, "artist": 'Pueblo', "title": 'Pueblo', "is_collection": False},
        {"kfjc_album_id": 736499, "artist": 'Various Artists', "title": 'Unknown Compilation', "is_collection": True}]

    for album in missing_albums:
        albums.create_album(
            kfjc_album_id=album["kfjc_album_id"], artist=album["artist"], 
            title=album["title"], is_collection=album["is_collection"])

def add_missing_playlists():
    """The playlist table is a swiss cheese of data voids causing import failures."""
    missing_playlists = [
        26, 27, 28, 29, 30, 31, 32, 33, 
        24509, 24511, 24513, 24516, 24518, 24519, 24520, 24521, 24522, 24523, 24524, 24525, 24526, 24527, 
        24528, 24530, 24750, 24752, 24753, 24755, 24757, 24567, 24772, 24773, 24775, 30008, 30054, 30067, 
        30270, 30973, 38296, 39715, 41100, 41101, 41368, 41539, 41704, 41729, 42354, 42500, 42523, 42580, 
        42662, 42829, 43031, 43271, 43272, 43507, 43538, 43659, 43800, 43869, 43899, 44069, 44254, 44285, 
        44286, 44397, 44541, 44775, 44807, 45221, 45354, 45477, 45478, 45479, 45480, 45481, 45482, 45483, 
        45497, 45512, 45522, 45533, 45630, 45698, 45699, 45729, 45795, 45796, 46105, 46149, 46271, 46370, 
        46372, 46576, 46689, 46812, 46813, 46962, 47065, 47262, 47330, 47448, 47449, 47450, 47553, 47665, 
        47751, 47805, 48014, 48089, 48184, 48185, 48350, 48429, 48453, 48480, 48490, 48506, 48613, 48614, 
        48664, 48740, 48751, 48772, 48802, 48979, 49011, 49120, 49216, 49425, 49426, 49439, 49465, 49610, 
        49718, 49833, 49912, 50016, 50017, 50018, 50188, 50852, 51156, 52603, 55156, 55993, 56002, 56052, 
        57516, 57541, 57655, 58153, 58249, 58406, 58669, 58670, 58873, 59317, 59318, 59319, 59344, 59539, 
        59621, 59622, 59623, 59624, 59625, 59862, 59863, 59928, 59929, 59930, 59982, 60118, 60119, 60120, 
        60121, 60436, 60674, 60687, 60805, 61144, 61598, 61669, 61957, 62003, 62026, 62029, 62030, 62031, 
        62004, 62341, 62575, 62665, 62786, 62811, 62847, 63045, 63063, 63518, 63530, 64316, 64513, 65013, 
        65584, 65682, 66253, 66466, 64514]

    for kfjc_playlist_id in missing_playlists:
        playlists.create_playlist(
            kfjc_playlist_id=kfjc_playlist_id, dj_id=-1, 
            air_name=None, start_time=None, end_time=None)

# -=-=-=-=-=-=-=-=-=-=-=- Import the 5 CSV Files -=-=-=-=-=-=-=-=-=-=-=-

PLAYLIST_DATA_PATH = 'station_data/playlist.csv'
PLAYLIST_TRACK_DATA_PATH = 'station_data/playlist_track.csv'
ALBUM_DATA_PATH = 'station_data/album.csv'
TRACK_DATA_PATH = 'station_data/track.csv'
COLLECTION_TRACK_DATA_PATH = 'station_data/coll_track.csv'

def create_playlists(row):
    """Add all playlists rows."""

    # If we have one or the other, we can estimate the other:
    fixed_start_time, fixed_end_time = fix_playlist_times(
        start_time=row[3], end_time=row[4])
    # But if both are missing, we can get rid of the row. There are only
    # 14 rows out of 66k that are bad this way.

    # Map the bad Dr. Doug dj_id to the good one:
    # (-1391, 'Dr Doug', datetime.datetime(2019, 11, 26, 2, 1, 15))
    # (391, 'dr doug', datetime.datetime(2020, 6, 16, 1, 54, 9))
    # (-1391, 1)  TODO didn't work.

    if coerce_imported_data(row[1]) == -1391:
        row[1] = 391  # Reassign it.

    # Fix air_name of DJ CLICK:     DJ Click, Click, ^
    # 47690,47946,324,DJ Click,2015-01-20 21:57:03.000000,2015-01-21 02:00:26.000000
    # 47759,48016,324,Click,2015-01-30 06:06:30.000000,2015-01-30 09:58:55.000000
    # 48671,48944,324,^,2015-06-08 21:59:44.000000,2015-06-09 02:08:35.000000
    if coerce_imported_data(row[2]) in ['Click', '^']:
        row[2] = 'DJ Click'  # Reassign it.

    # Toss the row with kfjc_playlist_id = 0; that was the incomplete show
    # at the time of the database dump.
    kfjc_playlist_id = coerce_imported_data(row[0])

    if fixed_start_time and fixed_end_time and kfjc_playlist_id:
        # Drop the 14 rows we can't make a question out of.
        # Import 2/15/22 still had these 15 rogue rows.
        playlists.create_playlist(
            kfjc_playlist_id=kfjc_playlist_id,
            dj_id=coerce_imported_data(row[1]),
            air_name=coerce_imported_data(row[2]),
            start_time=coerce_imported_data(fixed_start_time),
            end_time=coerce_imported_data(fixed_end_time))

def create_playlist_tracks(row):
    """Add all playlist_tracks rows."""

    album_title = coerce_imported_data(row[5])
    artist = coerce_imported_data(row[3])
    track_title = coerce_imported_data(row[4])

    if all(v is None for v in [album_title, artist, track_title]):
        # Not importing blank rows reduced the table size by
        # 282,167 rows (11%) and reduced import time by 50s:
        return

    kfjc_playlist_id = coerce_imported_data(row[0])
    indx = coerce_imported_data(row[1])
    kfjc_album_id = coerce_imported_data(row[6])
    time_played = coerce_imported_data(row[8])

    playlist_tracks.create_playlist_track(
        kfjc_playlist_id=kfjc_playlist_id,
        indx=indx, 
        kfjc_album_id=kfjc_album_id,
        album_title=album_title,
        artist=artist,
        track_title=track_title,
        time_played=time_played)

def create_albums(row):
    """Add all albums rows."""

    albums.create_album(
        kfjc_album_id=coerce_imported_data(row[0]),
        artist=coerce_imported_data(row[1]),
        title=coerce_imported_data(row[2]),
        is_collection=bool(row[7]))   # TODO: Bug here. they're all TRUE.

def create_collection_tracks(row):
    """Add all collection tracks rows."""

    tracks.create_track(
        kfjc_album_id=coerce_imported_data(row[0]),
        artist=coerce_imported_data(row[2]),
        title=coerce_imported_data(row[1]),
        indx=coerce_imported_data(row[3]))

def create_tracks(row):
    """Add all tracks rows without Artist."""

    tracks.create_track(
        kfjc_album_id=coerce_imported_data(row[0]),
        artist=None,
        title=coerce_imported_data(row[1]),
        indx=coerce_imported_data(row[3]))

# -=-=-=-=-=-=-=-=-=-=-=- Chunk Large Files for Import -=-=-=-=-=-=-=-=-=-=-=-

CHUNK_SIZE = 100000  # lines

def import_all_tables():
    """Import Station Data from csv files in chunks."""
    add_missing_albums()
    add_missing_playlists()
    db.session.commit()

    # Albums and PLaylists must be imported first since the other tables depend on them:
    data_path_and_function = [
        (ALBUM_DATA_PATH, create_albums),
        (PLAYLIST_DATA_PATH, create_playlists),
        (PLAYLIST_TRACK_DATA_PATH, create_playlist_tracks),
        (COLLECTION_TRACK_DATA_PATH, create_collection_tracks),
        (TRACK_DATA_PATH, create_tracks)]

    for each_tuple in data_path_and_function:
        file_path, row_handler = each_tuple  # unpack
        seed_a_large_csv(file_path=file_path, row_handler=row_handler)

def seed_a_large_csv(file_path, row_handler):
    """Large files must be broken into chunks."""

    num_loops = get_num_loops(file_path=file_path)

    for i in range(num_loops):
        print(f"\n\nNow attempting {file_path}, Loop {i+1} of {num_loops}:")
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

if __name__ == "__main__":    
    connect_to_db(app)
