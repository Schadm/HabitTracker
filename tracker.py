from datetime import date
from database import safe_tracking, get_challenge_for_habit, tracks_today, safe_streak, tracks_week, tracks_month


class Tracker:
    def __init__(self, user):
        """
        Class to track executed habits/actions into a tracker.
        :param user: Logged in user that tracks the action.
        """
        self.user = user
        self.habit = ""
        self.challengeID = ""
        self.period = ""
        self.interval = 0
        self.date_started = "2000-01-01"
        self.date = "2000-01-01"
        self.week = 1
        self.month = 1
        self.year = 2000
        self.db = ""
        
    def import_challenge(self, db, habit):
        """
        Function to import challenge information into the tracker object.
        An initiated tracker object that just contains the user will be filled in this function the other parameters.
        :param db: an initialized sqlite3 database connection
        :param habit: habit to which the challenge must be filtered.
        :return: none
        """
        self.habit = habit
        challenge = get_challenge_for_habit(db, self.user, self.habit)
        self.challengeID = challenge[0][0]
        self.period = challenge[0][3]
        self.interval = challenge[0][4]
        self.date_started = challenge[0][5]

    def safe_track(self, db, date_track):
        """
        Function to safe tracking information from track object into sqlite3 database.
        The function gives feedback on how many trackings are needed to reach streak.
        :param db:  an initialized sqlite3 database connection
        :param date_track: date for the to be tracked action
        :return: none
        """
        self.date = date_track
        date_str = str(date_track)
        date_split = date_str.split('-')
        self.week = date(int(date_split[0]), int(date_split[1]), int(date_split[2])).isocalendar().week
        self.month = int(date_split[1])
        self.year = int(date_split[0])
        safe_tracking(db, self.date, self.challengeID, self.week, self.month, self.year)
        tracked = 0

        """
        The following block checks the "Tracker" table in the database for the number of trackings per period
        (daily, weekly, monthly). The number of trackings per period is safed into ht "tracked" variable.
        """
        if self.period == "daily":
            tracked = tracks_today(db, self.challengeID, self.date)
        elif self.period == "weekly":
            tracked = tracks_week(db, self.challengeID, self.week, self.year)
        elif self.period == "monthly":
            tracked = tracks_month(db, self.challengeID, self.month, self.year)
        """
        The following block checks the number of trackings per period saved in the "tracked" variable.
        It is checked against the specific number in the "interval" variable of the given object.
        In case of a streak, it is saved into the "Streak" table. Then a result text is printed.
        """
        if tracked == self.interval:
            print("Streak! Well done. Come back soon!")
            safe_streak(db, self.challengeID, self.date, self.week, self.month, self.year)
        elif tracked > self.interval:
            print("Streak already reached before, but keep on tracking")
        else:
            print(f"{self.interval - tracked} more to go.")
