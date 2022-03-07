"""Common operations for KFJC Trivia Robot."""

import json
import collections
from datetime import date
from sqlalchemy.sql.expression import func, distinct

from model import db, connect_to_db


def get_count(table_dot_column, unique=True):
    """A fast row counter."""

    if unique:
        return db.session.query(
            func.count(distinct(table_dot_column))).scalar()
    else:
        return db.session.query(func.count(table_dot_column)).scalar()


def get_ages(table_dot_column):
    """Get oldest and newest date in a column."""

    oldest = db.session.query(func.min(table_dot_column)).first()[0]
    newest = db.session.query(func.max(table_dot_column)).first()[0]
    return (oldest, newest)


def print_a_query_reply(sql_alchemy_object):
    """Print results during development."""

    length = 0
    for i in sql_alchemy_object:
        print(i)
        length += 1
    print(f"{length} rows.")


def format_an_int_with_commas(your_int):
    """
    >>> format_an_int_with_commas(1000000)
    '1,000,000'
    """
    return f"{your_int:,}"


def make_date_pretty(date_time_string):
    """
    >>> make_date_pretty('2000-07-28')
    'July 28, 2000'
    """
    if isinstance(date_time_string, str):
        return date.fromisoformat(date_time_string).strftime('%B %d, %Y')
    else:  # Maybe it's a datetime_object
        return date_time_string.strftime('%B %d, %Y')


def minutes_to_years(minutes):
    """Report a duration like C-3PO would.

    >>> minutes_to_years(1000000)
    '1 years, 47 weeks, and 0 days'
    """
    number_of_days = minutes / (60 * 24)
    years = int(number_of_days / 365)
    weeks = int((number_of_days % 365) / 7)
    days = int((number_of_days % 365) % 7)

    return f"{years} years, {weeks} weeks, and {days} days"


def the_right_apostrophe(air_name):
    """So that questions can have a natural conversational tone.

    >>> air_name = "Oscar Hox"
    >>> s = the_right_apostrophe(air_name)
    >>> f"{air_name}{s}"
    "Oscar Hox's"

    >>> air_name = "Art Crimes"
    >>> s = the_right_apostrophe(air_name)
    >>> f"{air_name}{s}"
    "Art Crimes'"

    >>> air_name = "Spliff Skankin'"
    >>> s = the_right_apostrophe(air_name)
    >>> f"{air_name}{s}"
    "Spliff Skankin's"
    """

    if air_name[-1] in ['s']:
        return "'"
    elif air_name[-1] in ["'"]:
        # FIXED: Spliff Skankin''s first
        return "s"
    else:
        return "'s"


def open_json_files(file_path):
    """Open jsons, send back data."""

    with open(file_path) as f:
        data = json.load(f)

    return data


def convert_list_o_dicts_to_list_o_named_tuples(list_of_dicts):
    """After conversion, you'll be able to use dot notation on your data."""

    list_of_named_tuples = []

    for each_dict in list_of_dicts:
        converteted_dicts = convert_dict_to_named_tuple(each_dict)
        list_of_named_tuples.append(converteted_dicts)

    return list_of_named_tuples


def convert_dict_to_named_tuple(a_dict):
    """After conversion, you'll be able to use dot notation on your data."""

    return collections.namedtuple('GenericDict', a_dict.keys())(**a_dict)


if __name__ == '__main__':
    """Will connect you to the database when you run common.py interactively"""
    from server import app
    connect_to_db(app)

    import doctest
    doctest.testmod()  # python3 common.py -v
