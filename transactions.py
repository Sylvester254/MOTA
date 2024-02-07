import tkinter as tk
import datetime
import calendar
from tkinter import ttk, messagebox
from client import Client


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
        Retrieve transactions for each day in a selected month of a particular year, including client names.
        :param year: Integer representing the year.
        :param month: Integer representing the month.
        :return: A dictionary with date as key and a list of transaction tuples as value.
        """
        sql = '''SELECT t.date, t.id, t.client_id, t.amount, t.description, c.name
                 FROM transactions t
                 LEFT JOIN clients c ON t.client_id = c.id
                 WHERE strftime('%Y', t.date) = ?
                 AND strftime('%m', t.date) = ?
                 ORDER BY t.date'''
        cur = self.db_connection.conn.cursor()
        cur.execute(sql, (str(year), str(month).zfill(2)))
        daily_transactions = {}
        for row in cur.fetchall():
            date, transaction_id, client_id, amount, description, client_name = row
            if date not in daily_transactions:
                daily_transactions[date] = []
            daily_transactions[date].append((transaction_id, client_id, amount, description, client_name))
        return daily_transactions


class TransactionsPage(ttk.Frame):
    def __init__(self, parent, db_connection, go_back_callback):
        super().__init__(parent)

        self.db_connection = db_connection
        self.transaction_manager = Transaction(db_connection)
        self.client_manager = Client(db_connection)
        self.go_back_callback = go_back_callback

        # Container frame for year dropdown and add transaction button
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=10)

        # Add Transaction Button
        add_transaction_button = ttk.Button(control_frame, text="Add Transaction", command=self.open_add_transaction_form)
        add_transaction_button.pack(side=tk.LEFT, padx=(10, 0))

        # Dropdown to select year
        self.year_var = tk.StringVar()
        self.year_dropdown = ttk.Combobox(self, textvariable=self.year_var, state="readonly")

        # Populate the dropdown with years from 2010 to the current year
        current_year = datetime.datetime.now().year
        self.year_dropdown['values'] = [year for year in range(2010, current_year + 1)]
        self.year_dropdown.set(current_year)
        self.year_dropdown.pack()

        # Bind the selection event
        self.year_dropdown.bind("<<ComboboxSelected>>", self.on_year_selected)

        # Monthly totals list
        self.monthly_totals_tree = ttk.Treeview(self, columns=("Month", "Total"), show='headings')
        self.monthly_totals_tree.heading("Month", text="Month")
        self.monthly_totals_tree.heading("Total", text="Total")
        self.monthly_totals_tree.pack(expand=True, fill="both")

        # Bind selection event
        self.monthly_totals_tree.bind("<Double-1>", self.show_daily_transactions)

        # Go Back Button
        go_back_button = ttk.Button(self, text="Go Back", command=go_back_callback)
        go_back_button.pack(pady=10)

        # Initialize and load data for the current year
        current_year = str(datetime.datetime.now().year)
        self.year_var.set(current_year)
        self.load_monthly_totals(current_year)

        # Treeview for daily transactions
        self.daily_transactions_tree = ttk.Treeview(self, columns=("Date", "Amount", "Client", "Work Description"), show='headings')
        self.daily_transactions_tree.heading("Date", text="Date")
        self.daily_transactions_tree.heading("Amount", text="Amount")
        self.daily_transactions_tree.heading("Client", text="Client")
        self.daily_transactions_tree.heading("Work Description", text="Work Description")
        self.daily_transactions_tree.pack(expand=True, fill="both")

    def open_add_transaction_form(self):
        AddTransactionForm(self.winfo_toplevel(), self.transaction_manager, self.client_manager, self.refresh_callback)

    def refresh_callback(self):
        # Method to refresh transaction data display
        selected_year = int(self.year_var.get())
        self.load_monthly_totals(selected_year)

    def on_year_selected(self, event):
        """
        Load monthly totals for the selected year
        """
        selected_year = int(self.year_var.get())
        self.load_monthly_totals(selected_year)

    def load_monthly_totals(self, year):
        """
        Load and display monthly transaction totals for the given year.
        """
        # Clear existing data in the treeview
        for i in self.monthly_totals_tree.get_children():
            self.monthly_totals_tree.delete(i)

        # Fetch monthly totals
        monthly_totals = self.transaction_manager.get_monthly_totals(year)
        for month_num, total in monthly_totals.items():
            # Convert month number to month name
            month_name = calendar.month_name[int(month_num)]
            self.monthly_totals_tree.insert('', 'end', values=(month_name, total))

    def show_daily_transactions(self, event):
        selected_item = self.monthly_totals_tree.selection()[0]
        year = int(self.year_var.get())
        month = self.monthly_totals_tree.item(selected_item, 'values')[0]
        month_number = list(calendar.month_name).index(month)

        # Fetch and display daily transactions
        daily_transactions = self.transaction_manager.get_daily_transactions(year, month_number)
        for i in self.daily_transactions_tree.get_children():
            self.daily_transactions_tree.delete(i)

        for date, transactions in daily_transactions.items():
            for transaction in transactions:
                self.daily_transactions_tree.insert('', 'end', values=(date, transaction[2], transaction[4], transaction[3])) # date, amount, client, description


class AddTransactionForm:
    def __init__(self, parent, transaction_manager, client_manager, refresh_callback):
        self.window = tk.Toplevel(parent)
        self.window.title("Add New Transaction")
        self.window.geometry('300x400')

        self.transaction_manager = transaction_manager
        self.client_manager = client_manager
        self.refresh_callback = refresh_callback

        # Form fields
        ttk.Label(self.window, text="Date:").pack(pady=(10, 0))
        self.date_entry = ttk.Entry(self.window)
        self.date_entry.pack()

        ttk.Label(self.window, text="Amount:").pack()
        self.amount_entry = ttk.Entry(self.window)
        self.amount_entry.pack()

        ttk.Label(self.window, text="Description:").pack()
        self.description_entry = ttk.Entry(self.window)
        self.description_entry.pack()

        self.client_var = tk.StringVar()
        self.client_combobox = ttk.Combobox(self.window, textvariable=self.client_var, state="readonly")
        self.populate_client_dropdown()
        self.client_combobox.pack()

        # Submit button
        submit_button = ttk.Button(self.window, text="Submit", command=self.submit)
        submit_button.pack(pady=10)

    def populate_client_dropdown(self):
        clients = self.client_manager.get_all_clients()
        # Store clients as a list of tuples (client_name, client_id)
        self.clients_list = [(client[1], client[0]) for client in clients]  # Assuming name is client[1] and ID is client[0]
        self.client_combobox['values'] = [name for name, _ in self.clients_list]

    def submit(self):
        # Method to handle the submission of the form
        date = self.date_entry.get()
        amount = self.amount_entry.get()
        description = self.description_entry.get()
        client_name = self.client_var.get()
        client_id = next((id for name, id in self.clients_list if name == client_name), None)

        # Validate client selection
        if not client_name:  # Checks if a client name has not been selected
            messagebox.showwarning("Warning", "Please select a client.")
            return  # Exit the method to prevent further execution

        # Additional validation to ensure client_id was successfully retrieved
        if client_id is None:
            messagebox.showwarning("Warning", "Invalid client selected. Please select a valid client.")
            return

        try:
            self.transaction_manager.add_transaction(client_id, amount, date, description)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while adding the transaction: {e}")
        else:
            self.refresh_callback()  # Refresh the transactions list
            self.window.destroy()  # Close the form window
