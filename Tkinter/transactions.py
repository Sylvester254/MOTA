import tkinter as tk
import calendar
from tkinter import ttk, messagebox
from client import Client
from datetime import datetime


def is_valid_date(date_str):
    """
    Check if the date string matches the expected format ("YYYY-MM-DD").
    :param date_str: String representing the date entered on the form.
    :return: Boolean if date is valid or not
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


MAX_TRANSACTION_AMOUNT = 99000000


def is_valid_amount(amount_str):
    """
    Validate if the value is a number, it's non-negative and not exceeding maximum allowed amount for transactions.
    :param amount_str: String representing the amount entered in the form.
    :return: Boolean False if invalid amount and Float amount if valid.
    """
    try:
        amount = float(amount_str)
        return 0 <= amount <= MAX_TRANSACTION_AMOUNT
    except ValueError:
        return False


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

        # Container frame for year dropdown, label, and add transaction button
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=10, fill=tk.X)

        # Add Transaction Button
        add_transaction_button = ttk.Button(control_frame, text="Add Transaction", command=self.open_add_transaction_form)
        add_transaction_button.pack(side=tk.LEFT, padx=(20, 20))

        # Label for the year dropdown
        year_label = ttk.Label(control_frame, text="Filter by year:")
        year_label.pack(side=tk.LEFT, padx=(70, 0))

        # Dropdown to select year
        self.year_var = tk.StringVar()
        self.year_dropdown = ttk.Combobox(control_frame, textvariable=self.year_var, state="readonly")

        # Populate the dropdown with years from 2010 to the current year
        current_year = datetime.now().year
        self.year_dropdown['values'] = [year for year in range(2010, current_year + 1)]
        self.year_dropdown.set(current_year)  # Default to current year
        self.year_dropdown.pack(side=tk.LEFT)

        # Bind the selection event
        self.year_dropdown.bind("<<ComboboxSelected>>", self.on_year_selected)

        # Monthly totals list
        self.monthly_totals_tree = ttk.Treeview(self, columns=("Month", "Total Earnings"), show='headings')
        self.monthly_totals_tree.heading("Month", text="Month")
        self.monthly_totals_tree.heading("Total Earnings", text="Total Earnings")
        self.monthly_totals_tree.pack(expand=True, fill="both")

        # Bind selection event
        self.monthly_totals_tree.bind("<Double-1>", self.show_daily_transactions)

        # Go Back Button
        go_back_button = ttk.Button(self, text="Go Back", command=go_back_callback)
        go_back_button.pack(pady=5)

        # Initialize and load data for the current year
        current_year = str(datetime.now().year)
        self.year_var.set(current_year)
        self.load_monthly_totals(current_year)

        # Treeview for daily transactions
        self.daily_transactions_tree = ttk.Treeview(self, columns=("Date", "Amount", "Client", "Work Description"), show='headings')
        self.daily_transactions_tree.heading("Date", text="Date")
        self.daily_transactions_tree.heading("Amount", text="Amount")
        self.daily_transactions_tree.heading("Client", text="Client")
        self.daily_transactions_tree.heading("Work Description", text="Work Description")
        self.daily_transactions_tree.pack(expand=True, fill="both")

        # Right-click menu
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Edit", command=self.open_edit_transactions_form)
        self.popup_menu.add_command(label="Delete", command=self.trigger_delete_transactions)

        # Bind right-click event
        self.daily_transactions_tree.bind("<Button-2>", self.show_context_menu)  # For macOS
        self.daily_transactions_tree.bind("<Button-3>", self.show_context_menu)  # For Windows and Linux

    def show_context_menu(self, event):
        # Adjust to select the row under cursor
        row_id = self.daily_transactions_tree.identify_row(event.y)
        if row_id:
            self.daily_transactions_tree.selection_set(row_id)
            # Retrieve the tag for the selected item, which contains the transaction ID
            tags = self.daily_transactions_tree.item(row_id, 'tags')
            if tags:
                self.selected_transaction_id = tags[0]
                try:
                    self.popup_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    self.popup_menu.grab_release()

    def open_add_transaction_form(self):
        AddTransactionForm(self.winfo_toplevel(), self.transaction_manager, self.client_manager, self.refresh_callback, self.refresh_daily_transactions)

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
            rounded_total = round(total, 2)
            self.monthly_totals_tree.insert('', 'end', values=(month_name, rounded_total))

    def show_daily_transactions(self, event):
        selected_item = self.monthly_totals_tree.selection()[0]
        self.selected_year = int(self.year_var.get())  # Store selected year as a class attribute
        self.selected_month = self.monthly_totals_tree.item(selected_item, 'values')[0]  # Store selected month name
        month_number = list(calendar.month_name).index(self.selected_month)

        # Fetch and display daily transactions
        daily_transactions = self.transaction_manager.get_daily_transactions(self.selected_year, month_number)
        for i in self.daily_transactions_tree.get_children():
            self.daily_transactions_tree.delete(i)

        for date, transactions in daily_transactions.items():
            for transaction in transactions:
                # date, amount, client, description, transaction id
                self.daily_transactions_tree.insert('', 'end', values=(date, transaction[2], transaction[4], transaction[3]), tags=(transaction[0],))

    def refresh_daily_transactions(self):
        if hasattr(self, 'selected_year') and hasattr(self, 'selected_month'):
            month_number = list(calendar.month_name).index(self.selected_month)
            daily_transactions = self.transaction_manager.get_daily_transactions(self.selected_year, month_number)
            for i in self.daily_transactions_tree.get_children():
                self.daily_transactions_tree.delete(i)

            for date, transactions in daily_transactions.items():
                for transaction in transactions:
                    self.daily_transactions_tree.insert('', 'end',
                                                        values=(date, transaction[2], transaction[4], transaction[3]),
                                                        tags=(transaction[0],))

    def open_edit_transactions_form(self):
        transaction_id = self.selected_transaction_id
        # Open the EditTransactionForm
        EditTransactionForm(self.winfo_toplevel(), self.transaction_manager, self.client_manager, transaction_id, self.refresh_callback, self.refresh_daily_transactions)

    def trigger_delete_transactions(self):
        transaction_id = self.selected_transaction_id
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction? \n This move "
                                                 "cannot be undone"):
            self.transaction_manager.delete_transaction(transaction_id)
            self.refresh_callback()  # Refresh the monthly transactions display
            self.refresh_daily_transactions()  # Refresh daily transactions


class AddTransactionForm:
    def __init__(self, parent, transaction_manager, client_manager, refresh_callback, refresh_daily_transactions):
        self.window = tk.Toplevel(parent)
        self.window.title("Add New Transaction")
        self.window.geometry('300x400')

        self.transaction_manager = transaction_manager
        self.client_manager = client_manager
        self.refresh_callback = refresh_callback
        self.refresh_daily_transactions = refresh_daily_transactions

        # Form fields
        ttk.Label(self.window, text="Date(YYYY-MM-DD):").pack(pady=(10, 0))
        self.date_entry = ttk.Entry(self.window)
        self.date_entry.pack()

        ttk.Label(self.window, text="Amount(0 - 99,000,000):").pack()
        self.amount_entry = ttk.Entry(self.window)
        self.amount_entry.pack()

        ttk.Label(self.window, text="Description:").pack()
        self.description_entry = ttk.Entry(self.window)
        self.description_entry.pack()

        ttk.Label(self.window, text="Client:").pack()
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
        self.clients_list = [(client[1], client[0]) for client in clients]
        self.client_combobox['values'] = [name for name, _ in self.clients_list]

    def submit(self):
        # Method to handle the submission of the form
        date = self.date_entry.get()
        amount = self.amount_entry.get()
        description = self.description_entry.get()
        client_name = self.client_var.get()
        client_id = next((id for name, id in self.clients_list if name == client_name), None)

        # Perform validations
        if not is_valid_date(date):
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        if not is_valid_amount(amount):
            messagebox.showerror("Error", "Invalid amount. Enter amount between 0 and 99,000,000.")
            return

        if not client_name:
            messagebox.showwarning("Warning", "Please select a client.")
            return

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
            self.refresh_daily_transactions()
            self.window.destroy()  # Close the form window


class EditTransactionForm:
    def __init__(self, parent, transaction_manager, client_manager, transaction_id, refresh_callback, refresh_daily_transactions):
        self.client_id_by_name = None
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Transaction")
        self.window.geometry('300x400')

        self.transaction_manager = transaction_manager
        self.transaction_id = transaction_id
        self.client_manager = client_manager
        self.refresh_callback = refresh_callback
        self.refresh_daily_transactions = refresh_daily_transactions

        # Fetch transaction details using transaction_id
        transaction_details = self.transaction_manager.get_transaction(transaction_id)

        # Form fields
        ttk.Label(self.window, text="Date(YYYY-MM-DD):").pack(pady=(10, 0))
        self.date_entry = ttk.Entry(self.window)
        self.date_entry.insert(0, transaction_details[3])
        self.date_entry.pack()

        ttk.Label(self.window, text="Amount(0 - 99,000,000):").pack()
        self.amount_entry = ttk.Entry(self.window)
        self.amount_entry.insert(0, transaction_details[2])
        self.amount_entry.pack()

        ttk.Label(self.window, text="Description:").pack()
        self.description_entry = ttk.Entry(self.window)
        self.description_entry.insert(0, transaction_details[4])
        self.description_entry.pack()

        ttk.Label(self.window, text="Client:").pack()
        self.client_combobox = ttk.Combobox(self.window, state="readonly")
        # Populate combobox with client names and set the current client
        self.populate_client_dropdown(transaction_details[1])
        self.client_combobox.pack()

        # Submit button
        submit_button = ttk.Button(self.window, text="Update", command=self.submit)
        submit_button.pack(pady=10)

    def populate_client_dropdown(self, current_client_id):
        # Fetch all clients
        clients = self.client_manager.get_all_clients()
        client_names = []
        client_ids = []
        current_client_name = None

        for client in clients:
            # Assuming client structure is (client_id, client_name)
            client_id, client_name = client[0], client[1]
            client_names.append(client_name)
            client_ids.append(client_id)
            # Identify the current client's name
            if client_id == current_client_id:
                current_client_name = client_name

        # Populate the combobox
        self.client_combobox['values'] = client_names

        # Set the current client as the default selection
        if current_client_name:
            self.client_combobox.set(current_client_name)
        else:
            print("Current client not found.")

        # Store client IDs mapped by name for retrieval
        self.client_id_by_name = dict(zip(client_names, client_ids))

    def submit(self):
        # Extract form data
        date = self.date_entry.get()
        amount = self.amount_entry.get()
        description = self.description_entry.get()
        client_name = self.client_combobox.get()
        client_id = self.client_id_by_name.get(client_name)

        # Perform validations
        if not is_valid_date(date):
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        if not is_valid_amount(amount):
            messagebox.showerror("Error", "Invalid amount. Enter amount between 0 and 99,000,000.")
            return

        if not client_id:
            messagebox.showerror("Error", "Please select a valid client.")
            return

        # Update the transaction in the database
        try:
            self.transaction_manager.update_transaction(self.transaction_id, client_id, amount, date, description)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while updating the transaction: {e}")
        else:
            self.refresh_callback()  # Refresh monthly transactions display
            self.refresh_daily_transactions()  # Refresh daily transactions
            self.window.destroy()  # Close the form window

