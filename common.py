"""Common operations for KFJC Trivia Robot."""

from datetime import datetime, timedelta
from random import choice, randrange

from operator import itemgetter
from model import connect_to_db, db
from sqlalchemy.sql.expression import func, distinct

unix_zero_hour = "1969-12-31 16:00:00"

def get_count(table_dot_column, unique=True):
    """A fast row counter.
    
    Selecting an object by random key is faster than loading all 
    objects and choosing."""

    if unique:
        return db.session.query(func.count(distinct(table_dot_column))).scalar()
    else:
        return db.session.query(func.count(table_dot_column)).scalar()

def get_age(table_dot_column):
    oldest = db.session.query(func.min(table_dot_column)).first()[0]
    newest = db.session.query(func.max(table_dot_column)).first()[0]
    return (oldest, newest)

def get_age_by_dj_id(table_dot_column, dj_id):
    oldest = db.session.query(func.min(
        table_dot_column)).first()[0].strftime('%Y-%m-%d %H:%M:%S')
    newest = db.session.query(func.max(
        table_dot_column)).first()[0].strftime('%Y-%m-%d %H:%M:%S')
    return (oldest, newest)

def coerce_imported_data(one_cell):
    """Coerce incoming data to the correct type.
    >>> coerce_imported_data('NULL')
    >>> coerce_imported_data('Null')
    >>> coerce_imported_data("")
    >>> coerce_imported_data("0000-00-00 00:00:00")
    >>> coerce_imported_data(unix_zero_hour)
    >>> coerce_imported_data(-3)
    -3
    >>> coerce_imported_data(27)
    27
    >>> coerce_imported_data('Wave of the West, The ')
    'The Wave of the West'
    """

    if one_cell in [
        'NULL', "Null", '', " ", "?", ".", "..", "...", "*", "-", ",",
        "\"", "0000-00-00 00:00:00", unix_zero_hour, "1970-01-01 01:00:00"]:
        return None
    elif isinstance(one_cell, int):
        return int(one_cell)
    elif isinstance(one_cell, datetime):
        return datetime.fromisoformat(one_cell)
    else:
        return fix_titles(some_title=one_cell)

def time_shift(one_datetime_cell, shift=3):
    """
    >>> time_shift('2000-07-27 10:30:00')
    '2000-07-27 13:30:00'

    >>> time_shift('2000-07-27 10:30:00', -3)
    '2000-07-27 07:30:00'
    """

    return (datetime.fromisoformat(one_datetime_cell) + 
        timedelta(hours=shift)).strftime('%Y-%m-%d %H:%M:%S')

def fix_titles(some_title):
    """Fixes radio-station-naming-convention titles to English Readable titles.
    
    >>> fix_titles("Connick, Harry Jr.")
    'Harry Connick Jr.'
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

        #parts = some_title.split(",")
        # Incase there are 2 commas:
        #new_string = " ".join(parts[1:]) + " " + parts[0]
        #return new_string.strip()

    return some_title.strip()

def profanity_filter(title_string):
    """
    Radio station data. Found out I needed a Profanity Filter.

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
        "[coll]:", "").replace(
        "[Coll]:", "").replace(
        "  ", " ")

    return title_string


def fix_playlist_times(start_time, end_time):
    """A few dates are borked but if the other time cell is populated,
    we can make a decent guess. Fixes 166 rows.
    
    >>> fix_playlist_times(unix_zero_hour, unix_zero_hour)
    ('1969-12-31 16:00:00', '1969-12-31 16:00:00')
    >>> fix_playlist_times('2000-07-27 10:30:00', unix_zero_hour)
    ('2000-07-27 10:30:00', '2000-07-27 13:30:00')
    >>> fix_playlist_times(unix_zero_hour, '2000-07-27 10:30:00')
    ('2000-07-27 07:30:00', '2000-07-27 10:30:00')
    """

    if start_time == unix_zero_hour and end_time != unix_zero_hour:
        start_time = time_shift(end_time, shift=-3)
    elif end_time == unix_zero_hour and start_time != unix_zero_hour:
        end_time = time_shift(start_time, shift=3)
    
    return start_time, end_time

def minutes_to_years(minutes):
    number_of_days = minutes / (60 * 24)
    years = int(number_of_days / 365)
    weeks = int((number_of_days % 365) / 7)
    days = round((number_of_days % 365) % 7, 1)

    return f"{years} years, {weeks} weeks, and {days} days"

def sort_nested_lists(a_list_of_lists, by_key=0, reverse=False):

    a_list_of_lists = sorted(a_list_of_lists, key=itemgetter(by_key), reverse=reverse)
    return a_list_of_lists

def percent_correct(passed_count, failed_count):
    """For scorekeeping, leaderboards."""

    try:
        percent = round(float(passed_count) * 100 / (passed_count + failed_count), 1)
    except ZeroDivisionError:
        percent = 0.0
    return percent

def random_number_within_percent(target_number, percent=40, k=1):
    """ """
    high_value = int(target_number * (1 + (percent / 100)))
    low_value = int(target_number * (1 - (percent / 100)))
    if k != 1:
        random_numbers = []
        for _ in range(k):
            random_numbers.append(randrange(low_value, high_value))
        return random_numbers
    else:
        return randrange(low_value, high_value)

def random_date_surrounding_another_date(target_date_time, k=1):
    """Forget the time... just return a date.
    """
    #days_from_now = (datetime.now() - datetime.fromisoformat(target_date_time)).days
    days_from_now = (datetime.now() - target_date_time).days
    
    random_days = random_number_within_percent(target_number=days_from_now, percent=20, k=k)
    
    random_dates = []
    for dd in random_days:
        random_dates.append(make_date_pretty(date_time_string=(
            datetime.now() - timedelta(days=dd))))
    return random_dates

def random_time_delta(target_date_time, k=1):
    days_from_now = (datetime.now() - datetime.fromisoformat(target_date_time)).days
    
    random_days = random_number_within_percent(target_number=days_from_now, percent=20, k=k)

    random_time_deltas = []
    for dd in random_days:
        random_minutes = random_days * 24 * 60
        random_time_deltas.append(minutes_to_years(random_minutes))

    return random_time_deltas
    

def make_date_pretty(date_time_string):
    """
    >>> make_date_pretty('2000-07-28 06:00:00.000000')
    'July 28, 2000'
    """
    if isinstance(date_time_string, str):
        return datetime.fromisoformat(date_time_string).strftime('%B %d, %Y')
    else:  # Maybe it's a datetime_object
        return date_time_string.strftime('%B %d, %Y')


def top_n(popularity_dict, n=10):
    """Used to get Top10, Top40 lists from any popularity_dict.
    
    !!! May return more than n items in the event of a tie!!!
    """

    top_n_items = []

    highest_value = max_value_in_popularity_dict(
        popularity_dict=popularity_dict)

    for i in reversed(range(0, highest_value+1)):  # counting down...
        # Append all in category:
        for k in popularity_dict:
            if popularity_dict[k] >= i:
                # greater than equal to... will sortof work on floats, too.
                top_n_items.append(k)

        if len(top_n_items) >= n:
            break

    return top_n_items


def print_a_popularity_dict_in_order(popularity_dict, min_items_required=0):
    """See the results in order."""

    highest_value = max_value_in_popularity_dict(
        popularity_dict=popularity_dict)
    keys_and_frequencies = []  # An ordered list of most to least

    for i in reversed(range(min_items_required, highest_value+1)):
        # Counting Down:
        if i in popularity_dict.values():
            print(f"\n{i} occurrences:")
        for k in popularity_dict:
            if popularity_dict[k] == i:
                print(k)
                keys_and_frequencies.append((k, i))
    
    return keys_and_frequencies


def max_value_in_popularity_dict(popularity_dict):
    """What has the most plays, the most shows, the most anything?"""

    highest_value = popularity_dict[max(
        popularity_dict, key=popularity_dict.get)]
    return highest_value


if __name__ == '__main__':
    """Will connect you to the database when you run common.py interactively"""
    from server import app
    connect_to_db(app)

    import doctest
    doctest.testmod()  # python3 common.py -v