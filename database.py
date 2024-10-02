import sqlite3
from datetime import date


def get_db(name: str ="main.db"):
    """
    Creates and connects a database connection "main.db"
    :param name: name of the database/sql file with fixed name "main.db"
    :return: an initialized sqlite3 database connection
    """
    db = sqlite3.connect(name)
    create_tables(db)
    return db


def create_tables(db: str):
    """
    Creates 5 SQL tables: User, Habits, Challenges, Tracker, Streaks
    :param db: an initialized sqlite3 database connection
    :return: none
    """
    cur = db.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS User(
    Name TEXT PRIMARY KEY NOT NULL)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Habit(
    Name TEXT PRIMARY KEY NOT NULL,
    Description TEXT NOT NULL,
    Creation_Date Date NOT NULL,
    User_Created INTEGER NOT NULL,
    FOREIGN KEY (User_Created) REFERENCES User(User)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Challenges(
    Challenge_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    User TEXT NOT NULL,
    Habit TEXT NOT NULL,
    Period TEXT NOT NULL,
    Interval INTEGER NOT NULL,
    Start_Date Date NOT NULL,
    End_Date Date,
    FOREIGN KEY (User) REFERENCES User(Name),
    FOREIGN KEY (Habit) REFERENCES Habit(Name)
    )""")
    db.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS Tracker(
    Tracker_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ChallengeID INTEGER NOT NULL,
    Date Datetime NOT NULL,
    Week INTEGER NOT NULL,
    Month INTEGER NOT NULL,
    Year INTEGER NOT NULL,
    FOREIGN KEY (ChallengeID) REFERENCES Challenges(Challenge_ID)
    )""")
    db.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS Streaks(
    Streak_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ChallengeID INTEGER NOT NULL,
    Date Datetime NOT NULL,
    Week INTEGER NOT NULL,
    Month INTEGER NOT NULL,
    Year INTEGER NOT NULL,
    FOREIGN KEY (ChallengeID) REFERENCES Challenges(Challenge_ID)
    )""")
    db.commit()


def safe_user_name(db: str, name: str):
    """
    Function to check User table for existing username. In case it doesn't exist, a new username entry is created.
    :param db: an initialized sqlite3 database connection
    :param name: username to be safed in table
    :return: none
    """
    cur = db.cursor()
    cur.execute("""SELECT * FROM User WHERE name=(?)""", (name,))
    exists = len(cur.fetchall())
    if exists < 1:
        cur.execute("""INSERT INTO User (Name) VALUES (?)""", (name,))
        db.commit()


def get_user_names(db: str):
    """
    Function to list all created and stored usernames in sqlite3 database
    :param db: an initialized sqlite3 database connection
    :return: list of usernames
    """
    cur = db.cursor()
    cur.execute("""SELECT DISTINCT name FROM User""")
    data = cur.fetchall()
    return [elt[0] for elt in data]


def create_habit(db: str, name: str, description: str, user: str):
    """
    Checks the Habit table in the sqlite3 database for an already existing habit with the given name.
    In case the habit doesn't already exist, adds a new habit entry into the Habit table.
    It contains the habit name, a short description of the habit,
    a datestamp of the creation and logs the creating username.

    :param db: an initialized sqlite3 database connection
    :param name: name of the habit
    :param description: a short description of the habit
    :param user: the username that created the habit
    :return: none
    """
    cur = db.cursor()
    cur.execute("""SELECT * FROM Habit WHERE name=(?)""", (name,))
    exists = len(cur.fetchall())
    if exists < 1:
        current_date = date.today()
        cur.execute("""INSERT INTO Habit
        (Name, Description, Creation_Date, User_Created)
        VALUES (?,?,?,?)""", (name, description, current_date, user))
        db.commit()
        
        
def get_habits(db: str):
    """
    The function lists the habit names in the Habit table and returns it.
    :param db: an initialized sqlite3 database connection
    :return: list of habit names in the habit list
    """
    cur = db.cursor()
    cur.execute("""SELECT DISTINCT Name FROM Habit""")
    habit = cur.fetchall()
    return [elt[0] for elt in habit]


def get_habits_started(db: str, user: str):
    """
    The funktion lists the challenges in the Challenges table,
    that were started by the logged in user but not stopped, yet.
    The list is then returned.
    :param db: an initialized sqlite3 database connection
    :param user: logged in user, by whom the list will be filtered
    :return: list of habit names that with an entry in the Challenges table but were not stopped, yet.
    """
    cur = db.cursor()
    cur.execute("""SELECT Habit FROM Challenges WHERE End_Date ISNULL AND Challenges.user = (?)""", (user, ))
    habit = cur.fetchall()
    return [elt[0] for elt in habit]


def get_challenge_for_habit(db: str, user: str, habit: str):
    """
    Function to list and return all entries in Challenges table with a defined habit, stared by a defined user
    and where the challenge was not stopped yet (no end_date).
    :param db: an initialized sqlite3 database connection
    :param user: username that is checked for started challenges
    :param habit: habit for which the challenge list is to be filtered
    :return: list of filtered entries from Challenges table
    """
    cur = db.cursor()
    cur.execute("""SELECT * FROM Challenges WHERE Habit = (?) AND User = (?) AND End_Date IS NULL""", (habit, user))
    challenge = cur.fetchall()
    return challenge


def start_challenge(db: str, user: str, habit: str, period: str, interval: int):
    """
    Function to create an entry in the Challenges table of the sqlite3 database.
    The entry includes the habit name, the user who started the challenge, the periodicity and interval to be tracked
    and the actual data as the challenge start date.
    :param db: an initialized sqlite3 database connection
    :param user: user who started the challenge
    :param habit: the habit on which the challenge is based
    :param period: the periodicity of the habit to be tracked (e.g. daily)
    :param interval: The interval of the habit to be tracked (e.g. 2 times per period)
    :return: none
    """
    start_date = date.today()
    cur = db.cursor()
    cur.execute("""INSERT INTO Challenges
    (User, Habit, Period, Interval, Start_Date) VALUES (?,?,?,?,?)""", (user, habit, period, interval, start_date))
    db.commit()


def list_challenges(db: str, user: str):
    """
    Function to list all challenges of the logged in user in the Challenges table.
    :param db: an initialized sqlite3 database connection
    :param user: username to filter challenge entries
    :return: list of all challenges in the Challenges table filtered by user
    """
    cur = db.cursor()
    chall = cur.execute("""SELECT Challenge_ID, Habit, Period, Start_Date, End_Date FROM Challenges WHERE User = (?)""", (user,))
    return [elt for elt in chall]


def list_open_challenges(db: str, user: str):
    """
    Function to list all challenge entries in the Challenges table for the logged in user, that have no end date.
    :param db: an initialized sqlite3 database connection
    :param user: username to filter challenge entries
    :return: list of started but not ended challenges
    """
    cur = db.cursor()
    chall = cur.execute("""SELECT Habit, Period, Interval FROM Challenges WHERE User = (?) AND End_Date IS NULL """, (user,))
    return [elt for elt in chall]


def stop_challenge(db: str, user: str, habit: str):
    """
    Function to find a started entry in the Challenge table.
    The entry is filtered by habit, user and empty end date.
    After finding the entry, the current date is added as end date.
    :param db: an initialized sqlite3 database connection
    :param user: logged in user
    :param habit: the habit on which the challenge is based
    :return: none
    """
    end_date = date.today()
    cur = db.cursor()
    cur.execute("""UPDATE Challenges SET End_Date = (?) WHERE Habit = (?) AND User = (?)AND End_Date is NULL""",
                    (end_date, habit, user))
    db.commit()


def find_challenge_dates(db: str, challenge: int):
    """
    Function to extract start and end dates from a Challenge table entry.
    :param db: an initialized sqlite3 database connection
    :param challenge: unique identifier of challenge in database (challenge ID)
    :return: returns a list with start and end date for a given challenge
    """
    cur = db.cursor()
    cur.execute("""SELECT Start_Date, End_Date FROM Challenges WHERE Challenge_ID = (?)""",
                (challenge, ))
    dates = cur.fetchall()
    return dates[0][0], dates[0][1]


def find_challenges_by_period(db, user, period):
    """
    Function to filter and return challenge entries in the Challenge table by user and defined periodicity.
    :param db: an initialized sqlite3 database connection
    :param user: logged in user
    :param period: periodicity (daily, weekly or monthly) to filter challenge entries
    :return: list of filtered challenge entries
    """
    cur = db.cursor()
    chall = cur.execute("""SELECT Challenge_ID, Habit, Period, Interval, Start_Date FROM Challenges WHERE User = (?) AND Period = (?)""",
                        (user, period))
    return [elt for elt in chall]


def safe_tracking(db: str, date: date, challenge: int, week: int, month: int, year: int):
    """
    Function to safe information from tacker object into sqlite3 database.
    :param db: an initialized sqlite3 database connection
    :param date: tracking date
    :param challenge: unique identifier of challenge in database (challenge ID)
    :param week: week of tracking date
    :param month: month of tracking date
    :param year: year of tracking date
    :return: none
    """
    cur = db.cursor()
    cur.execute("""INSERT INTO Tracker (Date, ChallengeID, Week, Month, Year) VALUES (?,?,?,?,?)""",
                (date, challenge, week, month, year))
    db.commit()


def tracks_today(db: str, challenge: int, date: date):
    """
    Function to list tracking entries to a specific challenges that were tracked at the given date.
    :param db: an initialized sqlite3 database connection
    :param challenge: unique identifier of challenge in database (challenge ID)
    :param date:  tracking date
    :return: number of tracking entries for a given challenge at tracking date
    """
    cur = db.cursor()
    cur.execute("""SELECT * FROM Tracker WHERE ChallengeID = (?) AND Date = (?)""", (challenge, date))
    number = len(cur.fetchall())
    return number


def tracks_week(db: str, challenge: int, week: int, year: int):
    """
     Function to list tracking entries to a specific challenges that were tracked at the given week.
    :param db: an initialized sqlite3 database connection
    :param challenge: unique identifier of challenge in database (challenge ID)
    :param week: week of tracking date
    :param year: year of tracking date
    :return: number of tracking entries for a given challenge at week+year of tracking date
    """
    cur = db.cursor()
    cur.execute("""SELECT * FROM Tracker WHERE ChallengeID = (?) AND Week = (?) AND Year = (?)""",
                (challenge, week, year))
    number = len(cur.fetchall())
    return number


def tracks_month(db: str, challenge: int, month: int, year: int):
    """
    Function to list tracking entries to a specific challenges that were tracked at the given month.
    :param db: an initialized sqlite3 database connection
    :param challenge: unique identifier of challenge in database (challenge ID)
    :param month: month of tracking date
    :param year: year of tracking date
    :return: number of tracking entries for a given challenge at month+year of tracking date
    """
    cur = db.cursor()
    cur.execute("""SELECT * FROM Tracker WHERE ChallengeID = (?) AND Month = (?) AND Year = (?)""",
                (challenge, month, year))
    number = len(cur.fetchall())
    return number


def safe_streak(db: str, challenge: int, date: date,  week: int, month: int, year: int):
    """
    Function to safe accomplished streak entry in a challenge into the "Streaks" table
    :param db: an initialized sqlite3 database connection
    :param challenge: unique identifier of challenge in database (challenge ID)
    :param date: tracking date
    :param week: week of tracking date
    :param month: month of tracking date
    :param year: year of tracking date
    :return: none
    """
    cur = db.cursor()
    cur.execute("""INSERT INTO Streaks (Date, ChallengeID, Week, Month, Year) VALUES (?,?,?,?,?)""",
                (date, challenge, week, month, year))
    db.commit()


def find_streak(db: str, challenge: int, date: date):
    """
    Function to check Streaks table for a specific date for the status streak yes or no
    :param db: an initialized sqlite3 database connection
    :param challenge: unique identifier of challenge in database (challenge ID)
    :param date: date to check for a streak in table
    :return: streak yes or no at given date
    """
    cur = db.cursor()
    cur.execute("""SELECT * FROM Streaks WHERE ChallengeID = (?) AND Date = (?)""",
                (challenge, date))
    streak = cur.fetchall()
    check = "yes"
    if streak == []:
        check = "no"
    else:
        check = "streak"
    return check


def find_streak_week(db, challenge, week, year):
    """
    Function to check Streaks table for a week/year combination for the status streak yes or no
    :param db: an initialized sqlite3 database connection
    :param challenge: unique identifier of challenge in database (challenge ID)
    :param week: week to check for a streak in table
    :param year: year to check for a streak in table
    :return: streak yes or no at given date
    """
    cur = db.cursor()
    cur.execute("""SELECT * FROM Streaks WHERE ChallengeID = (?) AND Week = (?) AND Year = (?)""",
                (challenge, week, year))
    streak = cur.fetchall()
    check = "yes"
    if streak == []:
        check = "no"
    else:
        check = "streak"
    return check


def find_streak_month(db, challenge, month, year):
    """
    Function to check Streaks table for a month/year combination for the status streak yes or no
    :param db: an initialized sqlite3 database connection
    :param challenge: unique identifier of challenge in database (challenge ID)
    :param month: month to check for a streak in table
    :param year: year to check for a streak in table
    :return: streak yes or no at given date
    """
    cur = db.cursor()
    cur.execute("""SELECT * FROM Streaks WHERE ChallengeID = (?) AND Month = (?) AND Year = (?)""",
                (challenge, month, year))
    streak = cur.fetchall()
    check = "yes"
    if streak == []:
        check = "no"
    else:
        check = "streak"
    return check

