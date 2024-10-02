from database import create_habit


class Habit:
    def __init__(self, name: str, description: str, user: str):
        """
        Habit class constructor for habits to track
        :param name: name of the habit
        :param description: short description of the habit
        :param user: username that created the habit
        """
        self.name = name
        self.description = description
        self.user = user
        self.db = ""

    def store(self, db: str):
        """
        Store habit in database
        :param db: an initialized sqlite3 database connection
        """
        self.db = db
        create_habit(self.db, self.name, self.description, self.user)
