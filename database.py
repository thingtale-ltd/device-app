import sqlite3
import time

class DB:
    def __init__(self, dbpath="thingtale.db"):
        self.db_conn = sqlite3.connect(dbpath)
        self.db_cursor = self.db_conn.cursor()

        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS obj_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time INTEGER NOT NULL,
                data TEXT NOT NULL
            );''')

        self.db_conn.commit()

    def insert_obj(self, obj):
        timestamp_utc = int(time.time())
        self.db_cursor.execute("INSERT INTO obj_log (time, data) VALUES(?, ?);", (timestamp_utc, obj))
        self.db_conn.commit()
