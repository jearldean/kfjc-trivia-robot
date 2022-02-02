"""Common operations for KFJC Trivia Robot."""

import json
import time
#import datetime
from sqlalchemy.sql.expression import func, distinct  # select, 

from model import connect_to_db, db


def convert_datetime(datetime_object, human_readable=False):
    """Translates a datetime object into a string suitable for printing.
    
    Other formats:
    datetime_object.strftime("%m/%d/%Y, %H:%M:%S") # '01/19/2022, 22:08:42'
    datetime_object.strftime("%d %B, %Y") # '19 January, 2022'
    """
    if human_readable:
        return datetime_object.strftime("%A, %B %-d, %Y")
    else:
        return datetime_object.strftime("%m/%d/%Y, %H:%M:%S")


def open_json_files(file_path):
    """Open json files and return the data inside."""

    with open(file_path) as f:
        data = json.load(f)

    return data


def get_start_and_end_dates(date1, date2):
    """Returns a tuple: (earlier_date, later_date)
    
    Used to make sure date operations using innequality are always 
    in the right order."""

    if date1 > date2:  # early = date2 and later = date1
        return (date2, date1)
    else:  # early = date1 and later = date2
        return (date1, date2)


def time_stamp():
    """Call time_stamp() at the beginning and end of your function.
    Then use timer(start_time, end_time) to print the time elapased message.
    """
    return time.time()


def timer(start_time, end_time=None, operation=None):
    """Time the length of operations like importing data.
    
    timer() just diffs datetime objects.
    We could employ it to define ranges in the playlist data also."""

    if not end_time:  # Just stamp it now.
        end_time = time_stamp()
    elapsed_mins = (end_time - start_time) / 60
    print_minutes = round(elapsed_mins, 1)
    if not operation:
        operation = "That"

    print(f"{operation} took {print_minutes} minutes.")
    return print_minutes


def percent_correct(passed_count, failed_count):
    """For scorekeeping, leaderboards."""

    try:
        percent = round(float(passed_count) * 100 / (passed_count + failed_count), 1)
    except ZeroDivisionError:
        percent = 0.0
    return percent


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


def get_count(table_dot_column, unique=True):
    """A fast row counter.
    
    Selecting an object by random key is faster than loading all 
    objects and choosing."""

    if unique:
        return db.session.query(func.count(distinct(table_dot_column))).scalar()
    else:
        return db.session.query(func.count(table_dot_column)).scalar()


def when_is_this_from(table_dot_column, newest=True):
    """Get max age or min age of a column."""

    if newest:
        dto=db.session.query(table_dot_column.desc()).first()[0]
    else:
        dto=db.session.query(table_dot_column.desc()).first()[-1]

    return convert_datetime(datetime_object=dto)


if __name__ == '__main__':
    """Will connect you to the database when you run common.py interactively"""
    from server import app
    connect_to_db(app)
