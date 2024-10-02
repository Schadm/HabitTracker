from database import start_challenge, stop_challenge


class Challenge:
    def __init__(self, user: str, habit: str):
        """
        Challenge class constructor for started challenges
        :param user: User that started the challenge
        :param habit: Habit on which the challenge was based on
        """
        self.user = user
        self.habit = habit
        self.period = ""
        self.interval = ""
        self.db = ""

    def store(self, db: str, period: str, interval: int):
        """
        Function to store started challenge into sqlite database.
        :param db: an initialized sqlite3 database connection
        :param period: period in which the challenge is to be tracked
        :param interval: the interval in which the challenge is to be tracked
        :return: none
        """
        self.period = period
        self.interval = interval
        self.db = db
        start_challenge(self.db, self.user, self.habit, self.period, self.interval)

    def stop(self, db):
        """
        Function to stop a started challenge and store the stop date into sqlite database.
        :param db: an initialized sqlite3 database connection
        :return: none
        """
        self.db = db
        stop_challenge(self.db, self.user, self.habit)
