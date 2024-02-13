import sqlite3
from sqlite3 import Error


class DatabaseConnection:
    """
    This class will handle the connection to the SQLite database.
    """
    def __init__(self, db_file):
        """ Initialize db connection"""
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
            print(f"SQLite database connected: {db_file}")
        except Error as e:
            print(e)

    def create_table(self):
        """Create a table from the create_table_sql statement"""
        try:
            c = self.conn.cursor()
            c.execute(sql_create_clients_table)
            c.execute(sql_create_transactions_table)
            db.close_connection()
        except Error as e:
            print(e)

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

sql_create_transactions_table = """ CREATE TABLE IF NOT EXISTS transactions (
                                    id integer PRIMARY KEY,
                                    client_id integer NOT NULL,
                                    amount real NOT NULL,
                                    date text NOT NULL,
                                    description text,
                                    FOREIGN KEY (client_id) REFERENCES clients (id)
                                ); """


if __name__ == '__main__':
    database = "./finance_management.sqlite"

    # create a database connection and create tables
    db = DatabaseConnection(database)
    db.create_table()
