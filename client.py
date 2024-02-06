import sqlite3


class Client:
    def __init__(self, db_connection):
        """
        Initialize the Client class with a database connection.
        :param db_connection: Instance of DatabaseConnection to interact with the SQLite database.
        """
        self.db_connection = db_connection

    def add_client(self, name, phone_number, email, notes):
        """
        Add a new client to the clients table.
        :param name: String representing the client's name.
        :param phone_number: String representing the client's phone number.
        :param email: String representing the client's email address.
        :param notes: String containing additional notes about the client.
        :return: The row id of the created client record.
        """
        sql = ''' INSERT INTO clients(name, phone_number, email, notes)
                    VALUES(?, ?, ?, ?) '''
        cur = self.db_connection.conn.cursor()
        cur.execute(sql, (name, phone_number, email, notes))
        self.db_connection.conn.commit()
        return cur.lastrowid

    def get_client(self, client_id):
        """
        Retrieve a client by their ID.
        :param client_id: Integer representing the client's unique ID.
        :return: A tuple containing the client's data.
        """
        cur = self.db_connection.conn.cursor()
        cur.execute("SELECT * FROM clients WHERE id=?", (client_id,))
        return cur.fetchone()

    def update_client(self, client_id, name, phone_number, email, notes):
        """
        Update a client's information in the database.
        :param client_id: Integer representing the client's unique ID.
        :param name: String representing the client's name.
        :param phone_number: String representing the client's phone number.
        :param email: String representing the client's email address.
        :param notes: String containing additional notes about the client.
        """
        sql = ''' UPDATE clients
                    SET name = ?,
                        phone_number = ?,
                        email = ?,
                        notes = ?
                    WHERE id = ? '''
        cur = self.db_connection.conn.cursor()
        cur.execute(sql, (name, phone_number, email, notes, client_id))
        self.db_connection.conn.commit()

    def delete_client(self, client_id):
        """
        Delete a client by their ID from the database.
        :param client_id: Integer representing the client's unique ID.
        """
        sql = 'DELETE FROM clients WHERE id=?'
        cur = self.db_connection.conn.cursor()
        cur.execute(sql, (client_id,))
        self.db_connection.conn.commit()

