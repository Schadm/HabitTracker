import questionary
from habit import Habit
from challenge import Challenge
from tracker import Tracker
from database import (get_db, get_habits, get_user_names, safe_user_name, get_habits_started, list_challenges,
                      list_open_challenges, find_challenges_by_period)
from datetime import date, datetime
from analyse import list_streaks


def cli():
    db = get_db()

    stop = False

    while not stop:
        user_list = get_user_names(db)
        user_list.append("New name")
        user_list.append("Exit")

        user_selected = questionary.select(
            "What is your name?",
            choices=[elt for elt in user_list]).ask()

        if user_selected == "New name":
            new_user = questionary.text("Type in new name").ask()
            safe_user_name(db, new_user)
            user_selected = new_user

        if user_selected == "Exit":
            print("Bye")
            break

        task = questionary.select(
            "What do you want to do?",
            choices=["Track an action", "Start challenge", "Stop challenge",
                     "Create a new habit", "Analyse my tracking", "Exit"]).ask()

        if task == "Exit":
            print("Bye " + user_selected)
            break

        if task == "Track an action":
            """
            Task to track an executed action/habit.
            """
            habits_started = get_habits_started(db, user_selected)
            habits_started.append("Exit")
            habit_selected = questionary.select(
                "What is the habit you want to track?",
                choices=[elt for elt in habits_started]).ask()

            if not habit_selected == "Exit":
                date_answer = questionary.select("What is the date for tracking?",
                                                 choices=["Today", "Enter date"]).ask()
                date_selected = date.today()

                if date_answer == "Enter date":
                    while True:
                        try:
                            date_selected = datetime.strptime(questionary.text("Enter date (YYYY-MM-DD):").ask(),
                                                              "%Y-%m-%d").date()
                            if date_selected > date.today():
                                raise ValueError
                            break
                        except ValueError:
                            print("Invalid date. Try again")

                track = Tracker(user_selected)
                track.import_challenge(db, habit_selected)
                track.safe_track(db, date_selected)

                stop = True
                print("Thanks for tracking. Bye " + user_selected)

            else:
                print("Bye " + user_selected)
                break

        elif task == "Analyse my tracking":
            analysis = ((questionary.select
                        ("What do you want to analyze?",
                         choices=["Analyse specific challenge", "List started challenges",
                                  "List challenges with same periodicity", "Find challenge with longest streak",
                                  "Exit"]))
                        .ask())
            if analysis == "Exit":
                print("Bye " + user_selected)
                break

            if analysis == "Analyse specific challenge":
                """
                Task to chose a specific challenge of the logged in user.
                Prints a list of the tracking of the challenge by day, week or month.
                Adds the information whether a streak was reached in the given period.
                Finally lists the maximum number of streaks in a row for the given challenge.
                """
                chal_list = []
                chal_no = []
                chal_period = []
                challenges = list_challenges(db, user_selected)
                for chal in challenges:
                    chal_text = chal[1] + " ; " + chal[2] + " ; " + chal[3] + " ; " + str(chal[4])
                    chal_list.append(chal_text)
                chal_list.append("Exit")
                challenge_selected = questionary.select(
                    'What Challenge do you want to analyse '
                    '(Challenge ; Periodicity ; Date started ; Date stopped)?',
                    choices=[elt for elt in chal_list]).ask()

                if challenge_selected == "Exit":
                    print("Bye " + user_selected)
                    break
                else:
                    for chal in challenges:
                        chal_text = chal[1] + " ; " + chal[2] + " ; " + chal[3] + " ; " + str(chal[4])
                        if chal_text == challenge_selected:
                            chal_no = chal[0]
                            chal_period = chal[2]
                            break
                max_streak = list_streaks(db, chal_no, chal_period, "list")
                print(f"Your longest streak was {max_streak} in a row!")
                print("Bye " + user_selected)
                break

            if analysis == "List started challenges":
                """
                Task to list all challenges that are currently started and ongoing (without end date)
                """
                print("Habit ; Periodicity ; Tracking interval")
                challenges_started = list_open_challenges(db, user_selected)
                for elt in challenges_started:
                    print(elt)
                print("Bye " + user_selected)
                break

            if analysis == "List challenges with same periodicity":
                """
                Task to list all challenges, started by the logged in user with the chosen periodicity 
                (stopped or ongoing).
                """
                habit_period = questionary.select("Challenges of which period do you want to list?",
                                                  choices=["daily", "weekly", "monthly"]).ask()
                challenges_by_period = find_challenges_by_period(db, user_selected, habit_period)
                print("Challenge ID ; Habit ; Periodicity ; Interval ; Start date")
                for elt in challenges_by_period:
                    print(elt)
                print("Bye " + user_selected)
                break

            if analysis == "Find challenge with longest streak":
                """
                Task to print out a list of all challenges of the logged-in user with the maximum number of streaks
                in a row for that challenge.
                """
                challenges = list_challenges(db, user_selected)
                max_streaks = 0
                print("Habit / Periodicity / Start Date / End Date / Max No of Streaks in a Row")
                for chal in challenges:
                    chal_text = chal[1] + " ; " + chal[2] + " ; " + chal[3] + " ; " + str(chal[4])
                    chal_no = chal[0]
                    chal_period = chal[2]
                    streak_row = list_streaks(db, chal_no, chal_period, "no")
                    if max_streaks < streak_row:
                        max_streaks = streak_row
                    print(f"{chal_text} : Streaks in a row = {streak_row}")
                print(f"Your longest streaks in a row are {max_streaks} Streaks")
                print("Bye " + user_selected)
                break

        elif task == "Start challenge":
            """
            Task to start a challenge based on habits created by any user.
            The program lists all habits that the current user did not use to start a challenge.
            With that list, the user can choose a habit an start a challenge with personalized interval and periodicity.
            The program creates an object of the Challenge class and stores it into the database
            """
            habits_started = get_habits_started(db, user_selected)
            habit_list = get_habits(db)
            habits_not_started = set(habit_list) - set(habits_started)
            habits_not_started = list(habits_not_started)
            habits_not_started.append("Exit")
            if len(habits_not_started) == 1:
                print("All habits already started as a challenge.")
                stop = True
            else:
                habit_selected = questionary.select(
                    "What is the habit you want to track?",
                    choices=[elt for elt in habits_not_started]).ask()

                if not habit_selected == "Exit":
                    habit_period = questionary.select("On what period do you want to track your habit?",
                                                      choices=["daily", "weekly", "monthly"]).ask()
                    while True:
                        try:
                            habit_interval = int(questionary.text(
                                "How often do you want to track your habit in one period (x times "
                                + habit_period + ")?").ask())
                            break
                        except ValueError:
                            print("Invalid interval. Try again")

                    challenge = Challenge(user_selected, habit_selected)
                    challenge.store(db, habit_period, habit_interval)

                    stop = True
                    print("Thanks for starting your challenge. Come back soon for tracking!")

                else:
                    stop = True
                    print("Bye " + user_selected)

        elif task == "Stop challenge":
            """
            Lists all the habits where the user has a started challenge.
            By choosing a habit, the challenge will be stopped, so it cannot be tracked.
            Therefore an end date is added to the entry in the Challenge table in the database.
            """
            habits_started = get_habits_started(db, user_selected)
            habits_started.append("Exit")
            habit_selected = questionary.select(
                "What is the habit you want to stop tracking?",
                choices=[elt for elt in habits_started]).ask()

            if not habit_selected == "Exit":
                challenge = Challenge(user_selected, habit_selected)
                challenge.stop(db)

                stop = True
                print("Challenge stopped. Bye " + user_selected)
            else:
                stop = True
                print("Bye " + user_selected)

        elif task == "Create a new habit":
            """
            Task to create a new habit.
            The user is asked for a name for the habit to be created.
            Afterwards the user is asked for a short description of the habit to be created.
            With name and description a habit of the habit class is created and stored into the database.
            After creation, the program is ended.
            """
            habit_name = questionary.text("How do you want to call your habit you want to create?").ask()
            habit_desc = questionary.text("Please make a short description of your habit").ask()
            habit = Habit(habit_name, habit_desc, user_selected)
            habit.store(db)
            stop = True
            print("Thanks for adding a habit, " + user_selected + "!")
            print("Don't forget coming back for tracking")

        elif task == "Exit":
            stop = True
            print("Bye " + user_selected)


if __name__ == '__main__':
    cli()
