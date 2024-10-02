from database import get_db, safe_user_name
from analyse import list_streaks
from habit import Habit
from challenge import Challenge
from tracker import Tracker
from datetime import date


class TestTracker:

    def setup_method(self):
        """
        Function to set up test cases to test essential functions of the program.
        It sets up a test database and some fictional information like testuser, testhabit and testdetails.
        First a test user is set up and saved into the testdatabase
        """
        self.db = get_db("test.db")
        self.username = "Testname"
        self.habit_name = "Testhabit"
        self.habit_description = "Testhabitdescription"
        self.period = "daily"
        self.interval = 2
        self.tracking_date = date.today()

        safe_user_name(self.db, self.username)

    def test_habit(self):
        """
        In this function a test habit is set up and saved into the test database
        """
        habit = Habit(self.habit_name, self.habit_description, self.username)
        habit.store(self.db)

    def test_challenge_tracker(self):
        """
        Function to set up and start a test challenge and make 2 trackings.
        Afterwards, the streak datatable is checked for the automated streak check.
        """
        challenge = Challenge(self.username, self.habit_name)
        challenge.store(self.db, self.period, self.interval)

        tracker = Tracker(self.username)
        tracker.import_challenge(self.db, self.habit_name)
        tracker.safe_track(self.db, self.tracking_date)
        tracker.safe_track(self.db, self.tracking_date)

        challenge.stop(self.db)

        streakcounter = list_streaks(self.db, 1, self.period, "")
        assert streakcounter == 1

    def teardown_method(self):
        """
        Closure and removal of the test database.
        """
        self.db.close()
        import os
        os.remove("test.db")
