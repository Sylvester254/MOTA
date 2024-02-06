import sqlite3
from sqlite3 import Error


class DatabaseConnection:
    def __init__(self, db_file):
        """ Initialize db connection"""
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
            print(f"SQLite database connected: {db_file}")
        except Error as e:
            print(e)

    def create_table(self, create_table_sql):
        """Create a table from the create_table_sql statement"""
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


if __name__ == '__main__':
    database = "./mota.sqlite"

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

    # create a database connection and create tables
    db = DatabaseConnection(database)
    db.create_table(sql_create_clients_table)
    db.create_table(sql_create_transactions_table)
    db.close_connection()
