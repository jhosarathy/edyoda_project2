from Question import Question
from ScoreCard import ScoreCard
import time
import datetime

class User:
    def __init__(self, name, email_id, pswd, is_super, user_id=""):
        self.name = name
        self.email_id = email_id
        self.pswd = pswd
        self.is_super = is_super
        self.id = user_id
        self.table_name = "users"

    @classmethod
    def create_table(cls, db):
        return db.create_table("users", {
            "name": "text",
            "email_id": "text unique",
            "pswd": "text",
            "is_super": "integer"
        }, indexes=[["email_id"]])

    def create(self, db):
        (err, user_id) = db.insert_row(self.table_name, {
            "name": self.name,
            "email_id": self.email_id,
            "pswd": self.pswd,
            "is_super": self.is_super
        })
        if (err is not None) and ("UNIQUE constraint failed" in err):
            return (f"USER_ALREADY_EXISTS_ERR: {self.email_id}", user_id)
   
        return (None, user_id)

    def take_quiz(self, user, topic, level, db):
        (err, qsns) = Question.read_qsns_quiz(topic, level, db)
        if err is not None:
            return (err, None)

        score = 0
        for i, qsn in enumerate(qsns):
            print(f"\nQuestion{i+1}: {qsn.qsn}")
            for k, v in qsn.options.items():
                print(f"{k}. {v}")

            valid_ans = False
            while(not valid_ans):
                print("Ans: ")
                user_ans = input()
                if(user_ans in qsn.options):
                    valid_ans = True
                    if user_ans == qsn.ans:
                        score += 1
                        print("Correct!")
                    else:
                        print(f"Wrong! Correct ans: {qsn.ans}")
                else:
                    print(f"Enter a valid option!")           

        print(f"User score: {score}")
        scoreCard = ScoreCard(user.id, topic, level, score)
        (err, res) = scoreCard.create(db)
        if err is not None:
            print(f"SCORECARD_CREATE_ERR: {err}")
        else:
            print(f"ScoreCardID: {res}")

    def check_results(self, db):
        err, rows = db.read_rows("scorecards", "*", {"user_id": self.id})
        if err is not None:
            return (err, None)
        
        # print(rows)
        output = f"Topic\tLevel\tScore\tAttemptedAt\n"
        for i, s in enumerate(rows):
            at = datetime.datetime.fromtimestamp(int(s[5]))
            output = output + f"{s[2]}\t{s[3]}\t{s[4]}\t{at}\n"
        print(output)

    @classmethod
    def login(cls, email_id, pswd, db):
        err, rows = db.read_rows("users", "*", {"email_id": email_id})
        if err is not None:
            return (err, None)
        
        if len(rows) == 0:
            return (f"USER_NOT_FOUND: {email_id}", None)
        if rows[0][3] is not None and rows[0][3] != pswd:
            return (f"PSWD_WRONG_FOR: {email_id}", None)

        return (None, User(rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][0]))
