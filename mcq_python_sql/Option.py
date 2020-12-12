class Option:
    def __init__(self, qid, key, value):
        self.qid = qid
        # key examples: A, B, C, D
        self.key = key
        # value examples: "Not a string", "Object", "Pointer"
        self.value = value
        self.table_name = "options"

    @classmethod
    def create_table(cls, db):
        return db.create_table("options", {
            "qid": "text",
            "key": "text",
            "value": "text"
        }, foreign_key_references={"qid": ("questions", "id")}, uniqs=["qid,key"], indexes=[["qid"], ["key"]])

    def create(self, db):
        (err, qsn_id) = db.insert_row(self.table_name, {
            "qid": self.qid,
            "key": self.key,
            "value": self.value
        })
        if (err is not None) and ("UNIQUE constraint failed" in err):
            return (f"OPTION_ALREADY_EXISTS_ERR: QID {self.qid}, KEY {self.key}", res)
    
        return (None, qsn_id)
