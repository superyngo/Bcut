import sqlite3

class DatabaseManager:
    def __init__(self, db_path):
        self._db_path = db_path
        self._conn = None
        self._cursor = None

    @property
    def sqlite(self):
        if self._cursor is None:
            raise ConnectionError("Database is not connected. Call sqlite.setter with 'connect' first.")
        return self._cursor

    @sqlite.setter
    def sqlite(self, action="connect"):
        try:
            if action == "connect":
                if self._conn is None:
                    self._conn = sqlite3.connect(self._db_path)
                    self._cursor = self._conn.cursor()
                else:
                    print("Database is already connected.")
            elif action == "close":
                if self._conn is not None:
                    self._conn.close()
                    self._conn = None
                    self._cursor = None
                else:
                    print("Database is already closed.")
            else:
                raise ValueError("Invalid action. Use 'connect' or 'close'.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self._conn = None
            self._cursor = None
            raise

    def execute_query(self, query, parameters=None):
        try:
            if self._cursor is None:
                raise ConnectionError("Database is not connected. Call sqlite.setter with 'connect' first.")
            
            if parameters:
                self._cursor.execute(query, parameters)
            else:
                self._cursor.execute(query)
            
            self._conn.commit()
            return self._cursor.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred while executing the query: {e}")
            self._conn.rollback()
            raise

    def execute_many(self, query, parameters):
        try:
            if self._cursor is None:
                raise ConnectionError("Database is not connected. Call sqlite.setter with 'connect' first.")
            
            self._cursor.executemany(query, parameters)
            self._conn.commit()
            return self._cursor.rowcount
        except sqlite3.Error as e:
            print(f"An error occurred while executing the batch query: {e}")
            self._conn.rollback()
            raise
    def write_db(self, dbname:str, columns:list[str], records:list[list]):
        insert_replace_sql = f'''
        INSERT OR REPLACE INTO {dbname} (
            {','.join(columns)}
        ) VALUES ({",".join(["?"] * len(columns))})
        '''
        try:
            if self._cursor is None:
                raise ConnectionError("Database is not connected. Call sqlite.setter with 'connect' first.")
            
            self._cursor.executemany(insert_replace_sql, records)
            self._conn.commit()
            return self._cursor.rowcount
        except sqlite3.Error as e:
            print(f"An error occurred while executing the batch query: {e}")
            self._conn.rollback()
            raise
    def __enter__(self):
        self.sqlite = "connect"
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sqlite = "close"
