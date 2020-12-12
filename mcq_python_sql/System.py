from Singleton import Singleton
import os.path
from User import User
from Question import Question
from Option import Option
from Db import DB
from ScoreCard import ScoreCard


class System(Singleton):
    def __init__(self):
        db_path = "EdyodaQMS.db"
        summary = ""
        entities = [User, Question, Option, ScoreCard]
        names = ["users", "questions", "options", "scorecards"]
        if not os.path.exists(db_path):
            print(f"First time usage of this software. Creating database and tables")
            self.db = DB(db_path)
            for i, e in enumerate(entities):
                (err, res) = e.create_table(self.db)
                if err is not None:
                    print(f"CREATE_TABLE_ERR: ({names[i]}) {err}")

            # Preload data
            print("Preloading data for first time use...")
            self.preload_data(db)

            # Print summary of preloaded data

            superUser = User("Superuser EdyodaQMS", "ab", "cd", 1)
            superUser.create(self.db)

        else:
            self.db = DB(db_path)

        for i, e in enumerate(entities):
            err, rows = self.db.read_rows(names[i], "*", {})
            if err is not None:
                return (err, None)
            summary += f"{names[i]}: {len(rows)}\n"

        print(f"\nLoaded the following from database\n{summary}")
        

    def cli(self):
        loggedIn = False
        user = None
        while not loggedIn:
            print("\nLogin!")
            print("EmailID: ", end=" ")
            email_id = input()
            print("Pswd: ", end=" ")
            pswd = input()
            (err, user) = User.login(email_id, pswd, self.db)
            if err is not None:
                print(err)
            else:
                loggedIn = True

        cmds = []
        if user.is_super == 1:
            cmds = ["ADD_USER","ADD_QUESTION"]
        else:
            cmds = ["TAKE_QUIZ", "CHECK_RESULTS"]
        cmds.append("QUIT")

        quit = False
        while not quit:
            print(f"\nWelcome user {email_id}. Enter command")
            for i, c in enumerate(cmds):
                print(f"{i+1}. {c}")
            print("\nCommand: ", end="")
            cmd = input()
            if cmd.isnumeric() and int(cmd) < 4:
                cmd = cmds[int(cmd)-1]
                if cmd == "QUIT":
                    quit = True
                else:
                    self.process_cmd(cmd, user)
            else:
                print("Invalid command")
        print("Goodbye!")

    def process_cmd(self, cmd, user):
        if cmd == "ADD_USER":
            self.process_add_user(user)
        elif cmd == "ADD_QUESTION":
            self.process_add_question(user)
        elif cmd == "TAKE_QUIZ":
            self.process_take_quiz(user)
        elif cmd == "CHECK_RESULTS":
            user.check_results(self.db)
        else:
            pass

    def process_add_user(self, user):
        print("Name:", end=" ")
        name = input()
        print("Email:", end=" ")
        email = input()
        print("Pswd: ", end=" ")
        pswd = input()
        is_super = 0
        print("IsSuper (0/1):", end=" ")
        is_super = input()
        user = User(name, email, pswd, is_super)
        (err, res) = user.create(self.db)
        if err is not None:
            print(err)
        else:
            print(f"USER_ADDED_SUCCESSFULLY: (UserID {res})")

    def process_add_question(self, user):
        print("Topic:", end=" ")
        topic = input()
        print("Level (Easy, Medium, Hard):", end=" ")
        level = input()
        if (level not in ["Easy", "Medium", "Hard"]):
            print(f"Invalid level {level}")
            return
        print("Qsn: ", end=" ")
        qsn = input()
        (err, qsns) = Question.read(topic, level, qsn, self.db)
        if err is None and qsns is not None and len(qsns) > 0:
            print(f"QUESTION_ALREADY_PRESENT: {qsns}")
            return
        options = {}
        done = False
        ch = 0
        while not done:
            print("Enter option (Enter DONE when over):", end=" ")
            val = input()
            if val == "DONE":
                done = True
            else:
                key = str(chr(ord('A') + ch))
                options[key] = val
                ch += 1
        print('\n'.join(list(map(lambda x: f"{x[0]}. {x[1]}", options.items()))))
        print("\nEnter correct answer key: ", end="")
        ans = input()
        qsn = Question(topic, level, qsn, options, ans)
        (err, res) = qsn.create(self.db)
        if err is not None:
            print(err)
        else:
            print(f"QUESTION_ADDED_SUCCESSFULLY: (Question {res})")
    
    def process_take_quiz(self, user):
        print("Enter Topic: ", end="")
        topic = input()
        print("Enter Level: ", end="")
        level = input()
        (err, qsns) = Question.read(topic, level, "", self.db)
        if err is None and qsns is not None and len(qsns) > 0:
            user.take_quiz(user, topic, level, self.db)
            return
        else:
            print(f"TOPIC_NOT_FOUND: ({topic}, level {level})")

    def preload_data(self, db):
        with open("./data/users.tsv", 'r') as f:
            for line in f:
                line = line.strip()
                tokens = line.split("\t")
                user = User(tokens[0], tokens[1], tokens[2], tokens[3])
                user.create(db)
        with open("./data/questions.tsv", 'r') as f:
            for line in f:
                line = line.strip()
                tokens = line.split("\t")
                qsn = Question(tokens[0], tokens[1], tokens[2], {'A': tokens[3], 'B': tokens[4], 'C': tokens[5], 'D':tokens[6]}, tokens[7])
                qsn.create(db)
        with open("./data/scorecard.tsv", 'r') as f:
            for line in f:
                line = line.strip()
                tokens = line.split("\t")
                sc = ScoreCard(tokens[0], tokens[1], tokens[2], tokens[3], tokens[4])
                sc.create(db)
            


