"""Common operations for KFJC Trivia Robot."""

import json
import collections
from datetime import datetime, date  # date is used in a doctest.
from typing import List, Dict, Any, NamedTuple, Union
import sqlalchemy
from sqlalchemy.sql.expression import func, distinct

from model import db, connect_to_db


def get_count(table_dot_column: str, unique: bool = True) -> sqlalchemy:
    """A fast row counter."""

    if unique:
        return db.session.query(
            func.count(distinct(table_dot_column))).scalar()
    else:
        return db.session.query(func.count(table_dot_column)).scalar()


def get_ages(table_dot_column: str) -> List[str]:
    """Get oldest and newest date in a column."""

    oldest = db.session.query(func.min(table_dot_column)).first()[0]
    newest = db.session.query(func.max(table_dot_column)).first()[0]
    return (oldest, newest)


def format_an_int_with_commas(your_int: int) -> str:
    """
    >>> format_an_int_with_commas(1000000)
    '1,000,000'
    """
    return f"{your_int:,}"


def make_date_pretty(date_time_string: Union[datetime, str]) -> str:
    """
    >>> make_date_pretty('2022-02-01 00:03:33.000000')
    'Feb 1, 2022'
    >>> make_date_pretty(date(2010, 10, 8))
    'Oct 8, 2010'
    """
    if isinstance(date_time_string, str):
        date_time_string = datetime.strptime(
            date_time_string, "%Y-%m-%d %H:%M:%S.%f")
    return date_time_string.strftime('%b %-d, %Y')


def minutes_to_years(minutes: int) -> str:
    """Report a duration like C-3PO would.

    >>> minutes_to_years(10)
    ''
    >>> minutes_to_years(3000)
    '2 days'
    >>> minutes_to_years(10000)
    '6 days'
    >>> minutes_to_years(100000)
    '9 weeks, and 6 days'
    >>> minutes_to_years(1000000)
    '1 year, 47 weeks'
    >>> minutes_to_years(1060000)
    '2 years, and 6 days'
    >>> minutes_to_years(10000000)
    '19 years, 1 week, and 2 days'
    """
    statement = ""
    number_of_days = minutes / (60 * 24)
    years = int(number_of_days / 365)
    if years:
        statement += f"{years} year{pluralizer(years)}"
    weeks = int((number_of_days % 365) / 7)
    if years and weeks:
        statement += f", {weeks} week{pluralizer(weeks)}"
    elif weeks:
        statement += f"{weeks} week{pluralizer(weeks)}"
    days = int((number_of_days % 365) % 7)
    if weeks and days and statement:
        statement += f", and {days} day{pluralizer(days)} "
    elif (weeks and days) or (years and days):
        statement += f", and {days} day{pluralizer(days)} "
    elif days:
        statement += f"{days} day{pluralizer(days)} "

    return statement.strip()


def pluralizer(some_quantity: int) -> str:
    """Add the right suffix to nouns to sound right.

    >>> f"I have {1} doughnut{pluralizer(some_quantity=1)}."
    'I have 1 doughnut.'
    >>> f"I have {2} doughnut{pluralizer(some_quantity=2)}."
    'I have 2 doughnuts.'
    """
    plural = "" if some_quantity == 1 else "s"
    return plural


def the_right_apostrophe(air_name: str) -> str:
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


def open_json_files(file_path: str) -> List[Dict[str, Any]]:
    """Open jsons, send back data."""

    with open(file_path) as f:
        data = json.load(f)

    return data


def convert_list_o_dicts_to_list_o_named_tuples(
        list_of_dicts: List[Dict[str, Any]]) -> List[NamedTuple]:
    """After conversion, you'll be able to use dot notation on your data."""

    list_of_named_tuples = []

    for each_dict in list_of_dicts:
        converteted_dicts = convert_dict_to_named_tuple(each_dict)
        list_of_named_tuples.append(converteted_dicts)

    return list_of_named_tuples


def convert_dict_to_named_tuple(a_dict: Dict[str, Any]) -> NamedTuple:
    """After conversion, you'll be able to use dot notation on your data."""

    return collections.namedtuple('GenericDict', a_dict.keys())(**a_dict)


if __name__ == '__main__':
    """Will connect you to the database when you run common.py interactively"""
    from server import app
    connect_to_db(app)

    import doctest
    doctest.testmod()  # python3 common.py -v
