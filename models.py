import re
import sqlite3
from datetime import datetime


class Client:
    def __init__(self, client_id=None, name="", phone_number="", email="", notes=""):
        """
        Initialize a Client object.

        Args:
            client_id (int, optional): ID of an existing client. Defaults to None.
            name (str, optional): Client's name. Defaults to "".
            phone_number (str, optional): Client's phone number. Defaults to "".
            email (str, optional): Client's email address. Defaults to "".
            notes (str, optional): Additional notes about the client. Defaults to "".
        """
        self.client_id = client_id
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.notes = notes

    def validate_email(self):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, self.email):
            raise ValueError("Invalid email format.")

    def add_client(self, db_manager):
        """
        Add a new client to the clients table.

        Args:
            db_manager (DatabaseManager): Instance to interact with the database.

        Returns:
            int: The row ID of the newly created client record.
        """
        if not self.name:
            raise ValueError("Client name cannot be empty.")

        self.validate_email()

        sql = """INSERT INTO clients(name, phone_number, email, notes) 
                 VALUES(?, ?, ?, ?)"""
        params = (self.name, self.phone_number, self.email, self.notes)

        cursor = db_manager.execute_query(sql, params)
        self.client_id = cursor.lastrowid  # Assign generated ID to self
        return self.client_id

    @staticmethod
    def get_client(client_id, db_manager):
        """
        Retrieve a client by their ID.
        :param db_manager: (DatabaseManager) Instance to interact with the database.
        :param client_id: Integer representing the client's unique ID.
        :return: A tuple containing the client's data.
        """
        cursor = db_manager.execute_query("SELECT * FROM clients WHERE id=?", (client_id,))
        return cursor.fetchone()

    @staticmethod
    def get_all_clients(db_manager):
        """
        Retrieve all clients from the database.
        :param db_manager: (DatabaseManager) Instance to interact with the database.
        :return: A list of tuples containing all clients' data.
        """
        cursor = db_manager.execute_query("SELECT * FROM clients")
        return cursor.fetchall()

    def update_client(self, db_manager):
        """
        Update an existing client's information in the database.

        Args:
            db_manager (DatabaseManager): Instance to interact with the database.
        """
        # Requires a valid client_id to be set beforehand
        if not self.client_id:
            raise ValueError("Client ID is not set. Cannot update.")

        if not self.name:
            raise ValueError("Client name cannot be empty.")

        self.validate_email()

        sql = """UPDATE clients
                 SET name = ?,
                     phone_number = ?,
                     email = ?,
                     notes = ?
                 WHERE id = ?"""
        params = (self.name, self.phone_number, self.email, self.notes, self.client_id)
        db_manager.execute_query(sql, params)

    @staticmethod
    def has_records(client_id, db_manager):
        """
        Check if the client has any associated records.
        :param db_manager: (DatabaseManager) Instance to interact with the database.
        :param client_id: Integer representing the client's unique ID.
        :return: Boolean indicating whether the client has records.
        """
        cursor = db_manager.execute_query("SELECT COUNT(*) FROM income_records WHERE client_id = ?", (client_id,))
        return cursor.fetchone()[0] > 0

    @staticmethod
    def delete_client(client_id, db_manager):
        """
        Delete a client by their ID from the database.
        :param db_manager: (DatabaseManager) Instance to interact with the database.
        :param client_id: Integer representing the client's unique ID.
        """
        sql = 'DELETE FROM clients WHERE id=?'
        db_manager.execute_query(sql, (client_id,))


MAX_TRANSACTION_AMOUNT = 10000


class IncomeRecord:
    """Represents an income record in the finance management application."""

    def __init__(self, income_id=None, client_id=None, amount=None, date=None, description=""):
        """
        Initialize an IncomeRecord object.

        Args:
            income_id (int, optional): ID of an existing record. Defaults to None.
            client_id (int, optional): ID of the client associated with the record. Defaults to None.
            amount (float, optional): Amount of the income record. Defaults to None.
            date (str, optional): Date of the record (YYYY-MM-DD format). Defaults to None.
            description (str, optional): Description of the record. Defaults to "".
        """
        self.income_id = income_id
        self.client_id = client_id
        self.amount = amount
        self.date = date
        self.description = description

    def is_valid_amount(self):
        """
        Validate if the value is a number, it's non-negative and not exceeding maximum allowed amount for transactions.
        :return: Boolean False if invalid amount and Float amount if valid.
        """
        try:
            amount = float(self.amount)
            return 0 <= amount <= MAX_TRANSACTION_AMOUNT  # 10000
        except ValueError:
            return False

    def is_valid_date(self):
        """
        Check if the date string matches the expected format ("YYYY-MM-DD").
        :return: Boolean if date is valid or not
        """
        try:
            datetime.strptime(self.date, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def add_record(self, db_manager):
        """
        Add a new record to the income_records table.

        Args:
            db_manager (DatabaseManager): Instance to interact with the database.

        Returns:
            int: The row ID of the newly created income record.
        """
        if not self.client_id:
            raise ValueError("Client is required.")
        if not self.is_valid_amount():
            raise ValueError("Invalid amount.")
        if not self.is_valid_date():
            raise ValueError("Invalid date format.")

        sql = '''INSERT INTO income_records(client_id, amount, date, description)
                    VALUES(?, ?, ?, ?) '''
        cursor = db_manager.execute_query(sql, (self.client_id, self.amount, self.date, self.description))
        return cursor.lastrowid

    def get_record(self, db_manager):
        """
        Retrieve a record by its ID.
        Args:
            db_manager (DatabaseManager): Instance to interact with the database.

        Returns:
             A tuple containing the record's data.
        """

        cursor = db_manager.execute_query("SELECT * FROM income_records WHERE id=?", (self.income_id,))
        return cursor.fetchone()

    def update_record(self, db_manager):
        """
        Update a record's information in the database.
        Args:
            db_manager (DatabaseManager): Instance to interact with the database.
        """
        if not self.client_id:
            raise ValueError("Client is required.")
        if not self.is_valid_amount():
            raise ValueError("Invalid amount.")
        if not self.is_valid_date():
            raise ValueError("Invalid date format.")

        sql = '''UPDATE income_records
                SET client_id = ?,
                    amount = ?,
                    date = ?,
                    description = ?
                WHERE id = ? '''
        db_manager.execute_query(sql, (self.client_id, self.amount, self.date, self.description, self.income_id))

    @staticmethod
    def delete_record(income_id, db_manager):
        """
        Delete a record by its ID from the database.
        Args:
            income_id (int, optional): ID of an existing record.
            db_manager (DatabaseManager): Instance to interact with the database.
        """
        try:
            sql = 'DELETE FROM income_records WHERE id=?'
            db_manager.execute_query(sql, (income_id,))
        except sqlite3.Error as e:
            raise e

    @staticmethod
    def get_monthly_totals(year, db_manager):
        """
        Retrieve the total amount transacted for each month of the given year.
        Args:
            db_manager (DatabaseManager): Instance to interact with the database.

            year: Integer representing the year.
        Return:
            A dictionary with month as key and total amount as value.
        """

        sql = ''' SELECT strftime('%m', date) AS month, SUM(amount) AS total
                    FROM income_records
                    WHERE strftime('%Y', date) = ?
                    GROUP BY month '''
        cursor = db_manager.execute_query(sql, (str(year),))
        monthly_totals = {row[0]: row[1] for row in cursor.fetchall()}
        return monthly_totals

    @staticmethod
    def get_daily_records(year, month, db_manager):
        """
        Retrieve records for each day in a selected month of a particular year, including client names.
        Args:
            db_manager (DatabaseManager): Instance to interact with the database.

            year: Integer representing the year.

            month: Integer representing the month.
        Return:
            A dictionary with date as key and a list of record tuples as value.
        """
        sql = '''SELECT r.date, r.id, r.client_id, r.amount, r.description, c.name
                 FROM income_records r
                 LEFT JOIN clients c ON r.client_id = c.id
                 WHERE strftime('%Y', r.date) = ?
                 AND strftime('%m', r.date) = ?
                 ORDER BY r.date'''
        cursor = db_manager.execute_query(sql, (str(year), str(month).zfill(2)))
        daily_records = {}
        for row in cursor.fetchall():
            date, income_id, client_id, amount, description, client_name = row
            if date not in daily_records:
                daily_records[date] = []
            daily_records[date].append((income_id, client_id, amount, description, client_name))
        return daily_records
