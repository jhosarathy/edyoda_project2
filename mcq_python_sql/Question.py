from Option import Option


class Question:
    def __init__(self, topic, level, qsn, options, ans, qid=""):
        self.topic = topic
        self.level = level
        self.qsn = qsn
        self.options = options
        self.ans = ans
        self.table_name = "questions"

    @classmethod
    def create_table(cls, db):
        return db.create_table("questions", {
            "topic": "text",
            "level": "text",
            "qsn": "text",
            "ans": "text"
        }, uniqs=["topic,level,qsn"], indexes=[["topic"], ["level"], ["qsn"]])

    def create(self, db):
        if(self.ans not in self.options):
            return (f"Answer option {self.ans} not in {self.options.keys()}")

        (err, qsn_id) = db.insert_row(self.table_name, {
            "topic": self.topic,
            "level": self.level,
            "qsn": self.qsn,
            "ans": self.ans
        })
        if (err is not None) and ("UNIQUE constraint failed" in err):
            return (f"QUESTION_ALREADY_EXISTS_ERR: TOPIC {self.topic}, LEVEL {self.level}, QSN {self.qsn}, {err}", qsn_id)

        # Create multiple options according to current question's needs
        for k, v in self.options.items():
            op = Option(qsn_id, k, v)
            (err, op_id) = op.create(db)
            if err is not None:
                return (f"OPTION_CREATE_ERR: {err}", qsn_id)

        return (None, qsn_id)

    def delete(self, qid, db):
        return db.delete_row(self.table_name, {"id": qid})

    @classmethod
    def read(cls, topic, level, qsn, db):
        where_clauses = {"topic": topic, "level": level}
        if qsn != "":
            where_clauses["qsn"] = qsn
        err, rows = db.read_row("questions", "*", where_clauses)
        if err is not None:
            return (err, None)
        return (err, rows)

    @classmethod
    def read_qsns_quiz(cls, topic, level, db):
        cols = [
            "questions.id AS qid", 
            "questions.topic as topic",
            "questions.level as level",
            "questions.qsn as qsn",
            "questions.ans as ans",
            "options.key as key",
            "options.value as value"
        ]
        where_clauses = {
            "questions.topic": topic,
            "questions.level": level
        }
        join_clauses = {"id": "qid"}
        err, rows = db.read_rows("questions", cols, where_clauses, "options", join_clauses)
        if err is not None:
            return (err, None)
        
        qsns = {}
        for row in rows:
            if row[0] in qsns:
                qsns[row[0]].options[row[5]] = row[6]
            else:
                qsns[row[0]] = Question(row[1], row[2], row[3], {row[5]: row[6]}, row[4], row[0])

        return (err, list(qsns.values()))
            