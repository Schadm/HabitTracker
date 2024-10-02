from database import find_streak, find_challenge_dates, find_streak_week, find_streak_month
from datetime import date, timedelta, datetime


def list_streaks(db: str, challenge: int, period: str, listing: str):
    """
    Function to list streaks for a given challenge
    :param db: an initialized sqlite3 database connection
    :param challenge: unique identifier of challenge in database (challenge ID)
    :param period: period defined for specific challenge (daily, weekly, monthly)
    :param listing: if parameter is "list" the function will print readout of every challenge date
    :return: maximum number of streaks in a row for a challenge
    """
    streak_counter = 0
    streak_counter_max = 0

    start_end_dates = find_challenge_dates(db, challenge)
    start_date = start_end_dates[0]
    end_date = start_end_dates[1]

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    start_date_split = date_separator(start_date)
    start_date_week = start_date_split[0]
    start_date_month = start_date_split[1]
    start_date_year = start_date_split[2]

    if start_end_dates[1] is None:
        end_date = str(date.today())
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    end_date_split = date_separator(end_date)
    end_date_week = end_date_split[0]
    end_date_month = end_date_split[1]
    end_date_year = end_date_split[2]

    if period == "daily":
        check_date = start_date

        while check_date <= end_date:
            streak = find_streak(db, challenge, check_date)
            if streak == "streak":
                streak_counter += 1
            else:
                streak_counter = 0
            if streak_counter > streak_counter_max:
                streak_counter_max = streak_counter
            if listing == "list":
                print(check_date, streak)
            check_date += timedelta(days=1)

    elif period == "weekly":
        check_date = start_date_year, start_date_week
        check_end_date = end_date_year, end_date_week + 1
        while check_date != check_end_date:
            streak = find_streak_week(db, challenge, check_date[1], check_date[0])
            if streak == "streak":
                streak_counter += 1
            else:
                streak_counter = 0
            if streak_counter > streak_counter_max:
                streak_counter_max = streak_counter
            if listing == "list":
                print(("CW" + str(check_date[1]) + "-" + str(check_date[0])), streak)
            check_date = check_date[0], check_date[1]+1

    elif period == "monthly":
        check_date = start_date_year, start_date_month
        check_end_date = end_date_year, end_date_month + 1
        while check_date != check_end_date:
            streak = (find_streak_month(db, challenge, check_date[1], check_date[0]))
            if streak == "streak":
                streak_counter += 1
            else:
                streak_counter = 0
            if streak_counter > streak_counter_max:
                streak_counter_max = streak_counter
            if listing == "list":
                print("month: "+(str(check_date[1]) + "-" + str(check_date[0])), streak)
            check_date = check_date[0], check_date[1]+1

    return streak_counter_max


def date_separator(test_date: date):
    """
    Function to extract week, month and year of a date as number and returns it in a list.
    :param test_date: date to extract
    :return: list with week-, month- and year number extracted from date input
    """
    date_str = str(test_date)
    date_split = date_str.split('-')
    date_week = date(int(date_split[0]), int(date_split[1]), int(date_split[2])).isocalendar().week
    date_month = int(date_split[1])
    date_year = int(date_split[0])
    return date_week, date_month, date_year
