"""Import Station Data from csv Files."""

import re
import csv
import time
import itertools
from random import choice
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from server import app
from model import db, connect_to_db
import djs
import playlists
import playlist_tracks
import albums
import tracks

# -=-=-=-=-=-=-=-=-=-=-=- Clean up Data for Import -=-=-=-=-=-=-=-=-=-=-=-

BAD_TIMES = [
    "0000-00-00 00:00:00", "1970-01-01 01:00:00", "1969-12-31 16:00:00"]


def fix_playlist_times(start_time, end_time):
    """A few dates are borked but if the other time cell is populated,
    we can make a decent guess. Fixes 166 rows.

    >>> fix_playlist_times("1969-12-31 16:00:00", "1969-12-31 16:00:00")
    ('1969-12-31 16:00:00', '1969-12-31 16:00:00')
    >>> fix_playlist_times('2000-07-27 10:30:00', "1969-12-31 16:00:00")
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

    return (
        datetime.fromisoformat(one_datetime_cell) +
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
    >>> coerce_imported_data('-3')
    -3
    >>> coerce_imported_data(27)
    27
    >>> coerce_imported_data('Wave of the West, The ')
    'The Wave of the West'
    """

    try:
        return int(one_cell)
    except (ValueError, TypeError):
        pass

    if one_cell in [
            'NULL', "Null", '', " ", "?", ".", "..", "...", "*", "-", ",",
            "\""] + BAD_TIMES:
        return None  # No Data *IS* No Data.
    elif isinstance(one_cell, datetime):
        return datetime.fromisoformat(one_cell)
    else:
        # Strings go through the "String Fixer":
        return fix_titles(some_title=one_cell)


def fix_titles(some_title):
    """Fixes radio-station-naming-convention titles to English Readable titles.

    >>> fix_titles("Connick, Harry Jr.")
    'Harry Connick Jr.'
    >>> fix_titles("Brown, James")
    'James Brown'
    >>> fix_titles("Hendrix, Jimi Experience")
    'Jimi Hendrix Experience'
    """
    if not some_title:
        return

    some_title = profanity_filter(title_string=some_title)

    if ", the" in some_title.lower() or ",the" in some_title.lower():
        without_the = some_title.replace(
            ", the", "").replace(",the", "").replace(
                ", The", "").replace(",The", "")
        return f"The {without_the}".strip()
    elif "," in some_title:
        some_title = some_title.replace(",", " ")
        some_title = some_title.replace("  ", " ")
        parts = some_title.split(" ")
        # Swap the first 2 items. Keep everything else in the same order.
        parts[0], parts[1] = parts[1], parts[0]
        some_title = " ".join(parts)
    return some_title.strip()


def profanity_filter(title_string):
    """
    Data comes from an edgey Radio station:
    Found out I needed a Profanity Filter.

    >>> profanity_filter(title_string="Pussy")
    'P&#x128576;ssy'
    >>> profanity_filter(title_string="Shit")
    'Sh&#x128169;t'
    """
    emojis = [
        "&#x129296;", "&#x129323;", "&#x129325;",
        "&#x129300;", "&#x128526;", "&#x128520;"]
    replace_with_emoji = choice(emojis)
    title_string = title_string.replace(
        "Fuck", f"F{replace_with_emoji}ck").replace(
        "Shit", f"Sh&#x128169;t").replace(
        "Pussy", "P&#x128576;ssy").replace(
        "Cunt", "C&#x128576;nt").replace(
        "[coll]:", "").replace(  # Station shorthand for collaboration tracks.
        "[Coll]:", "").replace(
        "  ", " ").replace(
        "______________________________", "")

    return title_string.strip()

# -=-=-=-=-=-=-=-=-=-=-=- Import the 5 CSV Files -=-=-=-=-=-=-=-=-=-=-=-


DJ_DATA_PATH = 'station_data/user.csv'
ALBUM_DATA_PATH = 'station_data/album.csv'
PLAYLIST_DATA_PATH = 'station_data/playlist.csv'
PLAYLIST_TRACK_DATA_PATH = 'station_data/playlist_track.csv'
COLLECTION_TRACK_DATA_PATH = 'station_data/coll_track.csv'
TRACK_DATA_PATH = 'station_data/track.csv'


def create_djs(row):
    """Add all djs rows."""

    dj_id = coerce_imported_data(row[0])
    air_name = str(coerce_imported_data(row[2]))
    # administrative dj_ids represent station business and not
    # real people we should make questions out of:
    administrative = False
    if air_name == 'None':
        administrative = True
    if 'kfjc' in air_name.lower():
        administrative = True
    if dj_id in [104, 105, -1, 191, 164, 434, 445]:
        administrative = True
    silent_mic = False
    if row[9] == 'Y' or dj_id == 210:
        silent_mic = True  # For Djs that have escaped this mortal realm.

    djs.create_dj(
        dj_id=dj_id,
        air_name=air_name,
        administrative=administrative,
        silent_mic=silent_mic)


def add_a_missing_dj(dj_id, air_name):
    """Add a dummy dj row to avoid import conflicts."""
    if not air_name:
        air_name = "None"
    create_djs(
        row=[
            dj_id, None, air_name, None,
            None, None, None, None, None, "N"])
    db.session.commit()


def create_albums(row):
    """Add all albums rows."""

    kfjc_album_id = coerce_imported_data(row[0])
    artist = str(coerce_imported_data(row[1]))
    # Charlie Forsyth has an int for album name.
    title = str(coerce_imported_data(row[2]))
    is_collection = bool(coerce_imported_data(row[7]))
    title, artist, _ = fix_self_titled_items(
        album_title=title, artist=artist, track_title=None)

    albums.create_album(
        kfjc_album_id=kfjc_album_id,
        artist=artist,
        title=title,
        is_collection=is_collection)


def add_a_missing_album(kfjc_album_id, artist, album_title):
    """Add a dummy album row to avoid import conflicts."""

    row = [kfjc_album_id, artist, album_title, None, None, None, None, 1]
    create_albums(row=row)
    db.session.commit()


def create_playlists(row):
    """Add all playlists rows."""

    # If if time is blank but the other isn't,
    # we can improve the data by estimating the other time:
    fixed_start_time, fixed_end_time = fix_playlist_times(
        start_time=row[3], end_time=row[4])

    # Map the one bad Dr. Doug dj_id row to the good one:
    if row[1] == '-1391':
        row[1] = 391  # Reassign it.

    # Fix air_name of DJ CLICK:     DJ Click, Click, ^
    if coerce_imported_data(row[2]) in ['Click', '^']:
        row[2] = 'DJ Click'  # Reassign it.

    kfjc_playlist_id = coerce_imported_data(row[0])
    dj_id = coerce_imported_data(row[1])
    air_name = str(coerce_imported_data(row[2]))
    start_time = coerce_imported_data(fixed_start_time)
    end_time = coerce_imported_data(fixed_end_time)

    playlists.create_playlist(
        kfjc_playlist_id=kfjc_playlist_id,
        dj_id=dj_id,
        air_name=air_name,
        start_time=start_time,
        end_time=end_time)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

        # Fix rows that cause import trouble:
        if not djs.get_dj_id_by_id(dj_id=dj_id):
            add_a_missing_dj(dj_id=dj_id, air_name=air_name)

        # And try again; it should go through now:
        playlists.create_playlist(
            kfjc_playlist_id=kfjc_playlist_id,
            dj_id=dj_id,
            air_name=air_name,
            start_time=start_time,
            end_time=end_time)

        db.session.commit()


def add_a_missing_playlist(kfjc_playlist_id):
    """Add a dummy playlist row to avoid import conflicts."""
    row = [kfjc_playlist_id, 1, "Swiss Cheese", None, None]
    create_playlists(row=row)
    db.session.commit()


def fix_self_titled_items(album_title, artist, track_title):
    """S/T is shorthand for Self-Titled. Copy the artist or as much as we know.

    >>> fix_self_titled_items("S/T", 'Prince', None)
    ('Prince', 'Prince', 'Prince')
    >>> fix_self_titled_items("S/t ", None, None)
    (None, None, None)
    >>> fix_self_titled_items(" s/T", 'Prince', None)
    ('Prince', 'Prince', 'Prince')
    >>> fix_self_titled_items(None, 'Prince', " s/T ")
    ('Prince', 'Prince', 'Prince')
    >>> fix_self_titled_items('Prince', 'Prince', "s/t")
    ('Prince', 'Prince', 'Prince')
    >>> fix_self_titled_items(None, 'Prince', " S/t")
    ('Prince', 'Prince', 'Prince')
    >>> fix_self_titled_items('Prince', " S/t  ", None)
    ('Prince', 'Prince', 'Prince')
    >>> fix_self_titled_items(None, " S/T", 'Prince')
    ('Prince', 'Prince', 'Prince')
    >>> fix_self_titled_items('Prince', " s/t ", None)
    ('Prince', 'Prince', 'Prince')
    """
    regex_test = r"(^|\s)(S|s)\/(T|t)\b"
    if artist:
        if bool(re.match(regex_test, artist)):
            artist = None
    if album_title:
        if bool(re.match(regex_test, album_title)):
            album_title = None
    if track_title:
        if bool(re.match(regex_test, track_title)):
            track_title = None

    if not track_title:
        # track is unreliable, reassign track_title:
        if artist:
            track_title = artist
        else:
            track_title = album_title

    if not album_title:
        # album is unreliable, reassign album_title:
        if artist:
            album_title = artist
        else:
            album_title = track_title

    if not artist:
        # artist is unreliable, reassign artist:
        if album_title:
            artist = album_title
        else:
            artist = track_title

    return album_title, artist, track_title


def create_playlist_tracks(row):
    """Add all playlist_tracks rows."""

    album_title = str(coerce_imported_data(row[5]))
    artist = str(coerce_imported_data(row[3]))
    track_title = str(coerce_imported_data(row[4]))

    album_title, artist, track_title = fix_self_titled_items(
        album_title, artist, track_title)

    if all(v is None for v in [album_title, artist, track_title]):
        # Not importing blank rows reduced the table size by 11%.
        return

    kfjc_playlist_id = coerce_imported_data(row[0])
    indx = coerce_imported_data(row[1])
    kfjc_album_id = coerce_imported_data(row[6])
    time_played = coerce_imported_data(row[8])
    if not time_played:
        # 'Borrow' the time from the playlist.
        # An estimate is better than a NULL.
        try:
            time_played = playlists.get_playlist_by_id(
                kfjc_playlist_id=kfjc_playlist_id).start_time
        except AttributeError:  # Some start_times are still blank.
            pass

    playlist_tracks.create_playlist_track(
        kfjc_playlist_id=kfjc_playlist_id,
        indx=indx,
        kfjc_album_id=kfjc_album_id,
        album_title=album_title,
        artist=artist,
        track_title=track_title,
        time_played=time_played)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

        # Fix rows that cause import trouble:
        if not albums.get_album_by_id(kfjc_album_id=kfjc_album_id):
            add_a_missing_album(
                kfjc_album_id=kfjc_album_id, artist=artist,
                album_title=album_title)
        if not playlists.get_playlist_by_id(kfjc_playlist_id=kfjc_playlist_id):
            add_a_missing_playlist(kfjc_playlist_id=kfjc_playlist_id)

        # And try again; it should go through now:
        playlist_tracks.create_playlist_track(
            kfjc_playlist_id=kfjc_playlist_id,
            indx=indx,
            kfjc_album_id=kfjc_album_id,
            album_title=album_title,
            artist=artist,
            track_title=track_title,
            time_played=time_played)
        db.session.commit()


def create_collection_tracks(row):
    """Add all collection tracks rows."""

    kfjc_album_id = coerce_imported_data(row[0])
    artist = str(coerce_imported_data(row[2]))
    title = str(coerce_imported_data(row[1]))
    indx = coerce_imported_data(row[3])
    _, artist, title = fix_self_titled_items(None, artist, title)

    tracks.create_track(
        kfjc_album_id=kfjc_album_id,
        artist=artist,
        title=title,
        indx=indx)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

        # Fix rows that cause import trouble:
        add_a_missing_album(
            kfjc_album_id=kfjc_album_id, artist=artist,
            album_title=title)

        # And try again; it should go through now:
        tracks.create_track(
            kfjc_album_id=kfjc_album_id,
            artist=artist,
            title=title,
            indx=indx)
        db.session.commit()


def create_tracks(row):
    """Add all tracks rows without Artist."""

    kfjc_album_id = coerce_imported_data(row[0])
    title = str(coerce_imported_data(row[1]))
    indx = coerce_imported_data(row[3])

    album = albums.get_album_by_id(kfjc_album_id=kfjc_album_id)
    if album:
        artist = album.artist
    else:
        # Fix rows that cause import trouble:
        # If we can't get it from the album,
        # this table can't tell you the artist.
        artist = None
        add_a_missing_album(
            kfjc_album_id=kfjc_album_id, artist=artist,
            album_title=title)
        # track_title isn't the album_title but, it's a best guess.

    tracks.create_track(
        kfjc_album_id=kfjc_album_id,
        artist=artist,
        title=title,
        indx=indx)

    # We have handled the error upfont.

# -=-=-=-=-=-=-=-=-=-=-=- Chunk Large Files for Import -=-=-=-=-=-=-=-=-=-=-=-


CHUNK_SIZE = 100000  # lines


def import_all_tables():
    """Import Station Data from csv files in chunks."""

    # Albums and PLaylists must be imported first since
    # the other tables depend on them:
    data_path_and_function = [
        (DJ_DATA_PATH, create_djs),
        (ALBUM_DATA_PATH, create_albums),
        (PLAYLIST_DATA_PATH, create_playlists),
        (PLAYLIST_TRACK_DATA_PATH, create_playlist_tracks),
        (COLLECTION_TRACK_DATA_PATH, create_collection_tracks),
        (TRACK_DATA_PATH, create_tracks)]

    tic = time.perf_counter()
    # Importing takes 4 1/2 hours but it will handle all it's own errors.
    for each_tuple in data_path_and_function:
        file_path, row_handler = each_tuple  # unpack
        seed_a_large_csv(file_path=file_path, row_handler=row_handler)
    toc = time.perf_counter()
    hours = float((toc - tic)/3600)
    print(f"Importing Station Data took {hours:0.4f} hours.")


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
                # This points to each table's import function:
                row_handler(row)

        db.session.commit()  # Commit after each large chunk.


def get_num_loops(file_path):
    """Get the number of loops it will take to import a CSV
    file for a given CHUNK_SIZE."""

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

    import doctest
    doctest.testmod()  # python3 import_station_data.py -v
