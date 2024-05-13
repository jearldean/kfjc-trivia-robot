"""Import Station Data from csv Files."""

import re
import csv
import time
import itertools
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from typing import List, Any, Callable, Optional

from server import app
from model import db, connect_to_db
import djs
import playlists
import playlist_tracks
import albums
import tracks

# -=-=-=-=-=-=-=-=-=-=-=- Clean up Data for Import -=-=-=-=-=-=-=-=-=-=-=-

BIRTH_OF_SPIDEY = datetime(1995, 9, 19, 0, 0, 0)

DO_NOT_CHANGE = ['Listen, Whitey!  The Sounds of Black Power 1967-1974']

SILENT_MIC = [210]  # When someone passes, it can be psychologically difficult to flip this bit.


# Put dj_ids in here to help the process along.

def fix_playlist_times(start_time: str, end_time: str) -> tuple[Optional[datetime], Optional[datetime]]:
    """A few dates are borked but if the other time cell is populated,
    we can make a decent guess. Fixes 166 rows.
    """
    time_validity = [a_valid_time(a_datetime_str=start_time), a_valid_time(a_datetime_str=end_time)]

    if False not in time_validity:  # All Trues: Both dates are good.
        return start_time, end_time
    elif True in time_validity:  # At least one date is good, try to fix the other.
        if time_validity[0]:  # start_time is the good one.
            return start_time, time_shift(start_time, shift=3)
        else:
            return end_time, time_shift(end_time, shift=-3)
    else:  # Two Falses, none of this data is reliable.
        return None, None  # Remove all time deta.


def a_valid_time(a_datetime_str: str) -> bool:
    if not a_datetime_str:
        return False
    try:
        a_datetime_obj = datetime.strptime(a_datetime_str, '%Y-%m-%d %H:%M:%S')
        if a_datetime_obj < BIRTH_OF_SPIDEY or a_datetime_obj > datetime.today():
            return False
    except ValueError:
        return False
    return True


def time_shift(one_datetime_cell: str, shift: int = 3) -> datetime:
    """
    >>> time_shift('2000-07-27 10:30:00')
    '2000-07-27 13:30:00'
    >>> time_shift('2000-07-27 10:30:00', -3)
    '2000-07-27 07:30:00'
    """

    return (
            datetime.fromisoformat(one_datetime_cell) +
            timedelta(hours=shift)).strftime('%Y-%m-%d %H:%M:%S')


def coerce_imported_data(one_cell: Any) -> Any:
    """Coerce incoming data to the correct type.
    >>> coerce_imported_data('NULL')
    >>> coerce_imported_data('Null')
    >>> coerce_imported_data("")
    >>> coerce_imported_data("0000-00-00 00:00:00")
    '0000-00-00 00:00:00'
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

    throwaway_titles = [
        'NULL', "Null", '', " ", "?", ".", "..", "...", "*", "-", ",",
        "\"", "None.", "None", "(None)", "none", "none."]

    if one_cell in throwaway_titles:  # + BAD_TIMES:
        return None  # No Data *IS* No Data.
    elif isinstance(one_cell, datetime):
        return datetime.fromisoformat(one_cell)
    else:
        # Strings go through the "String Fixer":
        return fix_titles(some_title=one_cell)


def fix_titles(some_title: str) -> str:
    """Fixes radio-station-naming-convention titles to English Readable titles.

    >>> fix_titles("Connick, Harry Jr.")
    'Harry Connick Jr.'
    >>> fix_titles("Brown, James")
    'James Brown'
    >>> fix_titles("Hendrix, Jimi Experience")
    'Jimi Hendrix Experience'
    >>> fix_titles("Listen, Whitey!  The Sounds of Black Power 1967-1974")
    'Listen, Whitey!  The Sounds of Black Power 1967-1974'
    """
    if not some_title:
        return

    if some_title in DO_NOT_CHANGE:
        return some_title.strip()

    some_title = profanity_filter(title_string=some_title)

    if ", the" in some_title.lower() or ",the" in some_title.lower():
        without_the = some_title.replace(
            ", the", "").replace(",the", "").replace(
            ", The", "").replace(",The", "")
        return f"The {without_the}".strip()
    if "," in some_title:
        some_title = some_title.replace(",", " ")
        some_title = some_title.replace("  ", " ")
        parts = some_title.split(" ")
        # Swap the first 2 items. Keep everything else in the same order.
        parts[0], parts[1] = parts[1], parts[0]
        some_title = " ".join(parts)
    if "/" in some_title:
        some_title = some_title.replace("/", " ")  # Enclose in Backticks, a slash means a new column to SQL.
    return some_title.strip()


def profanity_filter(title_string: str) -> str:
    """
    Data comes from an edgey Radio station:
    Found out I needed a Profanity Filter.

    It's a real hoot to check these words into git.
    I'm sure the community takes a clinical view.

    >>> profanity_filter(title_string="PuSsy")
    'P&#128576;ssy'
    >>> profanity_filter(title_string="ShiT")
    'Sh&#128169;t'
    >>> profanity_filter(title_string="Shithouse")
    'Sh&#128169;thouse'
    >>> profanity_filter(title_string="shit house")
    'Sh&#128169;t house'
    >>> profanity_filter(title_string="[COLL]: Collection")
    'Collection'
    >>> profanity_filter(title_string="<COLL>: Collection")
    'Collection'
    >>> profanity_filter(title_string="<COLL> Collection")
    'Collection'
    >>> profanity_filter(title_string="Coll Collection")
    'Collection'
    """

    replacements = [
        (r"[Ff][Uu][Cc][Kk]", "F&#129296;ck"),
        (r"[Pp][Uu][Ss][Ss][Yy]", "P&#128576;ssy"),
        (r"[Ss][Hh][Ii][Tt]", "Sh&#128169;t"),
        (r"[Cc][Uu][Nn][Tt]", "C&#128576;nt"),
        (r"[Aa][Ss][Ss][Hh][0Oo][Ll][Ee]", "A$$hole"),
        (r"[Nn][Ii][Gg][Gg][Ee][Rr]", "N&#9994;&#127998;gger"),
        (r"\[[Cc][Oo][Ll][Ll]\]:?", ""),
        (r"\<[Cc][Oo][Ll][Ll]\>:?", ""),
        (r"[Cc][Oo][Ll][Ll]:?\b", "")]
    for pat, repl in replacements:
        title_string = re.sub(pat, repl, title_string)

    return title_string.strip()


# -=-=-=-=-=-=-=-=-=-=-=- Import the 5 CSV Files -=-=-=-=-=-=-=-=-=-=-=-


DJ_DATA_PATH = 'station_data/user.csv'
ALBUM_DATA_PATH = 'station_data/album.csv'
PLAYLIST_DATA_PATH = 'station_data/playlist.csv'
PLAYLIST_TRACK_DATA_PATH = 'station_data/playlist_track.csv'
COLLECTION_TRACK_DATA_PATH = 'station_data/coll_track.csv'
TRACK_DATA_PATH = 'station_data/track.csv'


def create_djs(row: List[Any]):
    """Add all djs rows."""

    dj_id = coerce_imported_data(row[0])
    air_name = str(coerce_imported_data(row[2]))
    # administrative dj_ids represent station business and not
    # real people we should make questions out of:
    administrative = False
    if air_name == 'DK Click':
        air_name = 'DJ Click'  # Honestly think this is a typo
    if air_name == 'None':
        administrative = True
    if 'kfjc' in air_name.lower():
        administrative = True
    if dj_id in [104, 105, -1, 191, 164, 434, 445]:
        administrative = True
    silent_mic = False
    if row[9] == 'Y' or dj_id in SILENT_MIC:  # (Sometimes they're not so quick to set this flag.)
        silent_mic = True  # For Djs that have escaped this mortal realm. 💀

    djs.create_dj(
        dj_id=dj_id,
        air_name=air_name,
        administrative=administrative,
        silent_mic=silent_mic)


def add_a_missing_dj(dj_id: int, air_name: str):
    """Add a dummy dj row to avoid import conflicts."""
    if not air_name:
        air_name = "None"
    create_djs(
        row=[dj_id, None, air_name, None, None, None, None, None, None, "N"])
    db.session.commit()


def create_albums(row: List[Any]):
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


def add_a_missing_album(kfjc_album_id: int, artist: str, album_title: str):
    """Add a dummy album row to avoid import conflicts."""

    row = [kfjc_album_id, artist, album_title, None, None, None, None, 1]
    create_albums(row=row)
    db.session.commit()


def create_playlists(row: List[Any]):
    """Add all playlists rows."""

    # If one time is blank but the other isn't,
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


def add_a_missing_playlist(kfjc_playlist_id: int):
    """Add a dummy playlist row to avoid import conflicts."""
    row = [kfjc_playlist_id, 1, None, None, None]
    create_playlists(row=row)
    db.session.commit()


def fix_self_titled_items(
        album_title: str, artist: str, track_title: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
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


def create_playlist_tracks(row: List[Any]):
    """Add all playlist_tracks rows.

    Don't import blank rows:
    >>> create_playlist_tracks([24506,57,"0","","","",0,'NULL','NULL'])
    >>> create_playlist_tracks([24858,36,"0",'NULL','NULL',"",0,'NULL','NULL'])
    """
    try:
        artist = coerce_imported_data(row[3])
        album_title = coerce_imported_data(row[5])
        track_title = coerce_imported_data(row[4])
    except IndexError:  #
        """ try fixing this later but whatever:
        FROM playlists 
        WHERE playlists.kfjc_playlist_id = %(pk_1)s
        2024-05-11 22:10:24,530 INFO sqlalchemy.engine.Engine [cached since 1290s ago] {'pk_1': 25920}
        2024-05-11 22:10:24,531 INFO sqlalchemy.engine.Engine INSERT INTO playlist_tracks (kfjc_playlist_id, indx, kfjc_album_id, album_title, artist, track_title, time_played) VALUES (%(kfjc_playlist_id)s, %(indx)s, %(kfjc_album_id)s, %(album_title)s, %(artist)s, %(track_title)s, %(time_played)s) RETURNING playlist_tracks.id_
        2024-05-11 22:10:24,531 INFO sqlalchemy.engine.Engine [cached since 1290s ago] {'kfjc_playlist_id': 25920, 'indx': 7, 'kfjc_album_id': 609713, 'album_title': 'Haunted Graffiti 2 The Doldrums Vital Pink', 'artist': 'Ariel Pink', 'track_title': 'strange fires', 'time_played': datetime.datetime(2006, 8, 18, 6, 13, 12)}
        2024-05-11 22:10:24,531 INFO sqlalchemy.engine.Engine COMMIT
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "/Users/jem/PyCharmProjects/kfjc-trivia-robot/seed_database.py", line 28, in nuclear_option
            kfjc.import_all_tables()
          File "/Users/jem/PyCharmProjects/kfjc-trivia-robot/import_station_data.py", line 535, in import_all_tables
            seed_a_large_csv(file_path=file_path, row_handler=row_handler)
          File "/Users/jem/PyCharmProjects/kfjc-trivia-robot/import_station_data.py", line 556, in seed_a_large_csv
            row_handler(row)
          File "/Users/jem/PyCharmProjects/kfjc-trivia-robot/import_station_data.py", line 389, in create_playlist_tracks
            album_title = coerce_imported_data(row[5])
        IndexError: list index out of range
        >>>
        """
        return

    if all(v is None for v in [album_title, artist, track_title]):
        # Not importing blank rows reduced the table size by 11%.
        return

    artist = str(artist)
    album_title = str(album_title)
    track_title = str(track_title)

    album_title, artist, track_title = fix_self_titled_items(album_title, artist, track_title)

    kfjc_playlist_id = coerce_imported_data(row[0])
    indx = coerce_imported_data(row[1])
    kfjc_album_id = coerce_imported_data(row[6])
    """Consider this: performance will be improved if we just use
    the playlist start_time for all question-making. More granularity
    than one day is not needed and this is a 3-hour window.
    """
    try:
        time_played = playlists.get_playlist_by_id(
            kfjc_playlist_id=kfjc_playlist_id).start_time
    except AttributeError:  # Some start_times are still blank.
        time_played = None

    playlist_tracks.create_playlist_track(
        kfjc_playlist_id=kfjc_playlist_id,
        indx=indx,
        kfjc_album_id=kfjc_album_id,
        album_title=str(album_title),
        artist=str(artist),
        track_title=str(track_title),
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


def create_collection_tracks(row: List[Any]):
    """Add all collection tracks rows."""

    try:
        kfjc_album_id = coerce_imported_data(row[0])
        artist = str(coerce_imported_data(row[2]))
        title = str(coerce_imported_data(row[1]))
        indx = coerce_imported_data(row[3])
        _, artist, title = fix_self_titled_items(None, artist, title)
    except IndexError:
        return

    """ Try fixing this one later:
    2024-05-11 23:17:27,585 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2024-05-11 23:17:27,585 INFO sqlalchemy.engine.Engine INSERT INTO tracks (kfjc_album_id, artist, title, indx) VALUES (%(kfjc_album_id)s, %(artist)s, %(title)s, %(indx)s) RETURNING tracks.id_
    2024-05-11 23:17:27,585 INFO sqlalchemy.engine.Engine [cached since 0.09069s ago] {'kfjc_album_id': 9111, 'artist': 'Juluka', 'title': "Nans'impi", 'indx': 6}
    2024-05-11 23:17:27,586 INFO sqlalchemy.engine.Engine COMMIT
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/jem/PyCharmProjects/kfjc-trivia-robot/seed_database.py", line 28, in nuclear_option
        kfjc.import_all_tables()
      File "/Users/jem/PyCharmProjects/kfjc-trivia-robot/import_station_data.py", line 561, in import_all_tables
        file_path, row_handler = each_tuple  # unpack
      File "/Users/jem/PyCharmProjects/kfjc-trivia-robot/import_station_data.py", line 582, in seed_a_large_csv
        # This points to each table's import function:
      File "/Users/jem/PyCharmProjects/kfjc-trivia-robot/import_station_data.py", line 482, in create_collection_tracks
        title = str(coerce_imported_data(row[1]))
    IndexError: list index out of range
    >>> 
    """

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


def create_tracks(row: List[Any]):
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

    # We have handled the error upfront.


# -=-=-=-=-=-=-=-=-=-=-=- Chunk Large Files for Import -=-=-=-=-=-=-=-=-=-=-=-


CHUNK_SIZE = 100000  # lines


def import_all_tables():
    """Import Station Data from csv files in chunks."""

    # Albums and Playlists must be imported first since
    # the other tables depend on them:
    data_path_and_function = [
        (DJ_DATA_PATH, create_djs),
        (ALBUM_DATA_PATH, create_albums),
        (PLAYLIST_DATA_PATH, create_playlists),
        (PLAYLIST_TRACK_DATA_PATH, create_playlist_tracks),
        (COLLECTION_TRACK_DATA_PATH, create_collection_tracks),
        (TRACK_DATA_PATH, create_tracks)]

    tic = time.perf_counter()
    # Importing takes hours, but it will handle all it's own errors.
    for each_tuple in data_path_and_function:
        file_path, row_handler = each_tuple  # unpack
        seed_a_large_csv(file_path=file_path, row_handler=row_handler)
    toc = time.perf_counter()
    hours = float((toc - tic) / 3600)
    print(f"Importing Station Data took {hours:0.4f} hours.")


def seed_a_large_csv(file_path: str, row_handler: Callable):
    """Large files must be broken into chunks."""

    num_loops = get_num_loops(file_path=file_path)

    for i in range(num_loops):
        print(f"\n\nNow attempting {file_path}, Loop {i + 1} of {num_loops}:")
        start_mark, end_mark = get_start_chunk_and_end_chunk_row_indexes(
            loop_number=i)

        with open(file_path, 'r') as file:
            reader = csv.reader(file)

            for row in itertools.islice(reader, start_mark, end_mark):
                # This points to each table's import function:
                row_handler(row)

        db.session.commit()  # Commit after each large chunk.


def get_num_loops(file_path: str) -> int:
    """Get the number of loops it will take to import a CSV
    file for a given CHUNK_SIZE."""

    num_lines = sum(1 for _ in open(file_path))
    num_loops = int(num_lines / CHUNK_SIZE) + 1
    print(f"It will take {num_loops} loops in {CHUNK_SIZE:,} line chunks.")
    return num_loops


def get_start_chunk_and_end_chunk_row_indexes(loop_number: int) -> tuple:
    """Identify the start and end rows for a data chunk to be imported."""

    if loop_number == 0:
        return 1, CHUNK_SIZE
    else:
        return loop_number * CHUNK_SIZE, (loop_number + 1) * CHUNK_SIZE


if __name__ == "__main__":
    connect_to_db(app)

    import doctest

    doctest.testmod()  # python3 import_station_data.py -v
