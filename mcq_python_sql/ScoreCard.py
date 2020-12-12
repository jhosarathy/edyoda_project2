import time


class ScoreCard:
    def __init__(self, user_id, topic, level, score, tm=0):
        self.user_id = user_id
        # key examples: A, B, C, D
        self.topic = topic
        # value examples: "Not a string", "Object", "Pointer"
        self.level = level
        self.score = score
        self.attempted_at = int(time.time())
        if tm != 0:
            self.attempted_at = tm
        self.table_name = "scorecards"

    @classmethod
    def create_table(cls, db):
        return db.create_table("scorecards", {
            "user_id": "integer",
            "topic": "text",
            "level": "text",
            "score": "integer",
            "attempted_at": "bigint"
        }, foreign_key_references={"user_id": ("users", "id")}, uniqs=[], indexes=[["user_id"]])

    def create(self, db):
        (err, attempt_id) = db.insert_row(self.table_name, {
            "user_id": self.user_id,
            "topic": self.topic,
            "level": self.level,
            "score": self.score,
            "attempted_at": self.attempted_at
        })
        if (err is not None) and ("UNIQUE constraint failed" in err):
            return (f"OPTION_ALREADY_EXISTS_ERR: QID {self.qid}, KEY {self.key}", res)
    
        return (None, attempt_id)
