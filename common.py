"""Common operations for KFJC Trivia Robot."""

import json
import time


def open_json_files(file_path):

    with open(file_path) as f:
        data = json.load(f)

    return data


def get_start_and_end_dates(date1, date2):
    """Returns a tuple: (earlier_date, later_date)"""
    if date1 > date2:
        #early = date2
        #later = date1
        return (date2, date1)
    else:
        #early = date1
        #later = date2
        return (date1, date2)

def time_stamp():
    """Call time_stamp() at the beginning and end of your function.
    Then use timer(start_time, end_time) to print the time elapased message.
    """
    return time.time()

def timer(start_time, end_time=None, operation=None):
    if not end_time:
        end_time = time_stamp()
    elapsed_mins = (end_time - start_time) / 60
    print_minutes = round(elapsed_mins, 1)
    if not operation:
        operation = "That"

    print(f"{operation} took {print_minutes} minutes.")

def percent_correct(passed_count, failed_count):
    try:
        percent = round(float(passed_count) * 100 / (passed_count + failed_count), 1)
    except ZeroDivisionError:
        percent = 0.0
    return percent


if __name__ == '__main__':
    """Will connect you to the database when you run common.py interactively"""
    from server import app
    connect_to_db(app)
