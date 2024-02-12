import sqlite3


class DatabaseManager:
    """
    This class will handle the connection to the SQLite database.
    """
    def __init__(self, db_path):
        """ Initialize db connection"""
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_path)
            self.create_tables()
            print(f"SQLite database connected: {db_path}")
        except sqlite3.Error as e:
            print(e)

    def create_tables(self):
        """Create a table from the create_table_sql statement"""

        try:
            cursor = self.execute_query("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [name for (name,) in cursor.fetchall()]
            if 'clients' not in tables:
                self.execute_query(sql_create_clients_table)
            else:
                print("client table exist.")
            if 'income_records' not in tables:
                self.execute_query(sql_create_income_records_table)
            else:
                print("income_records table exist.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def execute_query(self, query, params=None):
        """
        Helper for managing cursor lifecycle with 'with' blocks
        Args:
            query: SQL statement to execute
            params: Optional values to be used in the SQL statement

        """
        try:
            with self.conn:
                cursor = self.conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor
        except sqlite3.Error as e:
            raise e

    def close_connection(self):
        """Close database connection"""

        if self.conn:
            self.conn.close()


# SQL for creating tables
sql_create_clients_table = """ CREATE TABLE IF NOT EXISTS clients (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    phone_number text,
                                    email text,
                                    notes text
                                ); """

sql_create_income_records_table = """ CREATE TABLE IF NOT EXISTS income_records (
                                    id integer PRIMARY KEY,
                                    client_id integer NOT NULL,
                                    amount real NOT NULL,
                                    date text NOT NULL,
                                    description text,
                                    FOREIGN KEY (client_id) REFERENCES clients (id)
                                ); """
