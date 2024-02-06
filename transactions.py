class Transaction:
    def __init__(self, db_connection):
        """
        Initialize the Transaction class with a database connection.
        :param db_connection: Instance of DatabaseConnection to interact with the SQLite database.
        """
        self.db_connection = db_connection

    def add_transaction(self, client_id, amount, date, description):
        """
        Add a new transaction to the transactions table.
        :param client_id: Integer representing the ID of the client associated with the transaction.
        :param amount: Float representing the amount of the transaction.
        :param date: String representing the date of the transaction in YYYY-MM-DD format.
        :param description: String containing a description of the transaction.
        :return: The row id of the created transaction record.
        """
        sql = '''INSERT INTO transactions(client_id, amount, date, description)
                    VALUES(?, ?, ?, ?) '''
        cur = self.db_connection.conn.cursor()
        cur.execute(sql, (client_id, amount, date, description))
        self.db_connection.conn.commit()
        return cur.lastrowid

    def get_transaction(self, transaction_id):
        """
        Retrieve a transaction by its ID.
        :param transaction_id: Integer representing the transaction's unique ID.
        :return: A tuple containing the transaction's data.
        """

        cur = self.db_connection.conn.cursor()
        cur.execute("SELECT * FROM transactions WHERE id=?", (transaction_id,))
        return cur.fetchone()

    def update_transaction(self, transaction_id, client_id, amount, date, description):
        """
        Update a transaction's information in the database.
        :param transaction_id: Integer representing the transaction's unique ID.
        :param client_id: Integer representing the ID of the client associated with the transaction.
        :param amount: Float representing the amount of the transaction.
        :param date: String representing the date of the transaction in YYYY-MM-DD format.
        :param description: String containing a description of the transaction.
        """
        sql = '''UPDATE transactions
                SET client_id = ?,
                    amount = ?,
                    date = ?,
                    description = ?
                WHERE id = ? '''
        cur = self.db_connection.conn.cursor()
        cur.execute(sql, (client_id, amount, date, description, transaction_id))
        self.db_connection.conn.commit()

    def delete_transaction(self, transaction_id):
        """
        Delete a transaction by its ID from the database.
        :param transaction_id: Integer representing the transaction's unique ID.
        """
        sql = 'DELETE FROM transactions WHERE id=?'
        cur = self.db_connection.conn.cursor()
        cur.execute(sql, (transaction_id,))
        self.db_connection.conn.commit()

    def get_monthly_totals(self, year):
        """
        Retrieve the total amount transacted for each month of the given year.
        :param year: Integer representing the year.
        :return: A dictionary with month as key and total amount as value.
        """

        sql = ''' SELECT strftime('%m', date) AS month, SUM(amount) AS total
                    FROM transactions
                    WHERE strftime('%Y', date) = ?
                    GROUP BY month '''
        cur = self.db_connection.conn.cursor()
        cur.execute(sql, (str(year),))
        monthly_totals = {row[0]: row[1] for row in cur.fetchall()}
        return monthly_totals

    def get_daily_transactions(self, year, month):
        """
        Retrieve transactions for each day in a selected month of a particular year.
        :param year: Integer representing the year.
        :param month: Integer representing the month.
        :return: A dictionary with date as key and a list of transaction tuples as value.
        """
        sql = '''SELECT date, id, client_id, amount, description
                FROM transactions
                WHERE strftime('%Y', date) = ?
                AND strftime('%m', date) = ?
                ORDER BY date '''
        cur = self.db_connection.conn.cursor()
        cur.execute(sql, (str(year), str(month).zfill(2)))
        daily_transactions = {}
        for row in cur.fetchall():
            date, transaction_id, client_id, amount, description = row
            if date not in daily_transactions:
                daily_transactions[date] = []
            daily_transactions[date].append((transaction_id, client_id, amount, description))
        return daily_transactions
    
