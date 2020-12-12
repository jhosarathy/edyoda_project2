import sqlite3


class DB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def execute(self, query, values, query_type):
        c = self.cursor
        err = None
        res = None
        # print(f"Query \"{query}\" Values\"{values}\"")
        try:
            if values is not None:
                c.execute(query, values)
            else:
                c.execute(query)
            if query_type == "INSERT_ROW":
                self.conn.commit()
                res = c.lastrowid
            elif query_type == "READ_ROWS":
                res = c.fetchall()
            elif query_type == "READ_ROW":
                res = c.fetchone()
            else:
                self.conn.commit()
                res = c.fetchone()
        except sqlite3.Error as e:
            err = f"SQLITE_EXECUTE_ERR: ({query_type}) {e.args[0]}"

        return (err, res)

    def create_table(self, table_name, columns, foreign_key_references={}, uniqs=[], indexes=[]):
        query = f"CREATE TABLE {table_name} (id integer primary key autoincrement,"
        query = query + ",".join(list(map(lambda x: f"{x[0]} {x[1]}", columns.items())))
        if len(uniqs) > 0:
            query = query + ","
            query = query + ",".join(list(map(lambda x: f"UNIQUE({x})", uniqs)))
        if len(foreign_key_references) > 0:
            query = query + ","
            query = query + ",".join(list(map(lambda x: f"FOREIGN KEY ({x[0]}) REFERENCES {x[1][0]}({x[1][1]}) ON UPDATE CASCADE ON DELETE CASCADE", foreign_key_references.items())))
        query = query + ")"
        (err, res) = self.execute(query, None, "CREATE_TABLE")
        if err is not None:
            return (err, res)

        # Create the indexes
        # print(f"INDEXES: {indexes}")
        for i in indexes:
            # print(f"INDEXES: {i}")
            iname = "_".join(list(i))
            istr = ",".join(list(i))
            (err, r) = self.execute(f"CREATE INDEX idx_{table_name}_{iname} ON {table_name}({istr})", None, "CREATE_INDEX")
            if err is not None:
                return (err, r)
        return (err, res)

    # INSERT INTO TABLE_NAME(COL1,COL2..) VALUES(VAL1,VAL2,..)
    def insert_row(self, table_name, row):
        items = row.items()
        columns = list(map(lambda x: x[0], items))
        values = tuple(map(lambda x: x[1], items))
        cs = ",".join(columns)
        query = f"INSERT INTO {table_name}({cs}) VALUES("
        query = query + ",".join(list(map(lambda x: "?", values)))
        query = query + ")"
        return self.execute(query, values, "INSERT_ROW")

    # UPDATE TABLE TABLE_NAME SET COL1=VAL1,COL2=VAL2.. WHERE COL3=VAL3 AND COL4=VAL4;
    def update_row(self, table_name, update, wherecols):
        items = update.items()
        update_columns = list(map(lambda x: x[0], items))
        update_values = tuple(map(lambda x: x[1], items))

        witems = wherecols.items()
        where_columns = list(map(lambda x: x[0], witems))
        where_values = tuple(map(lambda x: x[1], witems))

        query = f"UPDATE TABLE {table_name} SET "
        query = query + ",".join(list(map(lambda x: f"{x}=?", update_columns)))
        query = query + " WHERE "
        query = query + " AND ".join(list(map(lambda x: "{x}=?", where_columns)))

        return self.execute(query, update_values + where_values, "INSERT_ROW")

    # DELETE FROM TABLE_NAME WHERE COL1=VAL1 AND COL2=VAL2..
    def delete_row(self, table_name, row):
        items = row.items()
        columns = list(map(lambda x: x[0], items))
        values = tuple(map(lambda x: x[1], items))
        query = f"DELETE FROM {table_name} WHERE "
        query = query + " AND ".join(list(map(lambda x: f"{x}=?", columns)))
        return self.execute(query, values, "DELETE_ROW")

    # SELECT * FROM TABLE_NAME1 WHERE COL1=VAL1 AND COL2=VAL2 ..
    # INNER JOIN TABLE_NAME2 ON TABLE_NAME1.COL1 = TABLE_NAME2.COL5
    def read_rows(self, table_name1, cols, where_clauses, table_name2="", join_clauses={}):
        items = where_clauses.items()
        where_columns = list(map(lambda x: x[0], items))
        where_values = tuple(map(lambda x: x[1], items))
        cols_str = ",".join(list(map(lambda x: x, cols)))

        query = f"SELECT {cols_str} FROM {table_name1} "
        if table_name2 != "":
            query = query + f" INNER JOIN {table_name2} ON "
            query = query + " AND ".join(list(map(lambda x: f"{table_name1}.{x[0]}={table_name2}.{x[1]}", join_clauses.items())))
        query = query + " "
        if len(where_columns) > 0: query = query + "WHERE "
        query = query + " AND ".join(list(map(lambda x: f"{x}=?", where_columns)))
        return self.execute(query, where_values, "READ_ROWS")

    # SELECT * FROM TABLE_NAME1 WHERE COL1=VAL1 AND COL2=VAL2 ..
    # INNER JOIN TABLE_NAME2 ON TABLE_NAME1.COL1 = TABLE_NAME2.COL5
    def read_row(self, table_name1, cols, where_clauses, table_name2="", join_clauses={}):
        items = where_clauses.items()
        where_columns = list(map(lambda x: x[0], items))
        where_values = tuple(map(lambda x: x[1], items))
        cols_str = ",".join(list(map(lambda x: x, cols)))

        query = f"SELECT {cols_str} FROM {table_name1} "
        if len(where_columns) > 0: query = query + "WHERE "
        query = query + " AND ".join(list(map(lambda x: f"{x}=?", where_columns)))
        if table_name2 != "":
            query = query + f" INNER JOIN {table_name2} ON "
            query = query + " AND ".join(list(map(lambda x: f"{table_name1}.{x[0]}={table_name2}.{x[1]}", join_clauses.items())))

        query = query + " LIMIT 1"
        return self.execute(query, where_values, "READ_ROW")