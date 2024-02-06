import tkinter as tk
from tkinter import ttk, messagebox


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

    def get_all_clients(self):
        """
        Retrieve all clients from the database.
        :return: A list of tuples containing all clients' data.
        """
        cur = self.db_connection.conn.cursor()
        cur.execute("SELECT * FROM clients")
        return cur.fetchall()

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

    def has_transactions(self, client_id):
        """
        Check if the client has any associated transactions.
        :param client_id: Integer representing the client's unique ID.
        :return: Boolean indicating whether the client has transactions.
        """
        cur = self.db_connection.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM transactions WHERE client_id = ?", (client_id,))
        return cur.fetchone()[0] > 0

    def delete_client(self, client_id):
        """
        Delete a client by their ID from the database.
        :param client_id: Integer representing the client's unique ID.
        """
        sql = 'DELETE FROM clients WHERE id=?'
        cur = self.db_connection.conn.cursor()
        cur.execute(sql, (client_id,))
        self.db_connection.conn.commit()


class ClientsPage(ttk.Frame):
    def __init__(self, parent, db_connection, go_back_callback):
        super().__init__(parent)

        self.client_manager = Client(db_connection)
        self.go_back_callback = go_back_callback

        # Add New Client Button
        add_client_button = ttk.Button(self, text="Add New Client", command=self.open_add_client_form)
        add_client_button.pack(pady=10)

        # Clients List (using Treeview)
        self.clients_tree = ttk.Treeview(self, columns=("#", "Name", "Phone", "Email", "Notes"), show='headings')
        self.clients_tree.pack(expand=True, fill="both")

        # Define headings
        for col in self.clients_tree['columns']:
            self.clients_tree.heading(col, text=col)

        # Load clients data into the list
        self.load_clients_data()

        # Right-click menu
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Edit", command=self.open_edit_client_form)
        self.popup_menu.add_command(label="Delete", command=self.trigger_delete_client)

        # Bind right-click event
        self.clients_tree.bind("<Button-2>", self.show_context_menu)  # For macOS
        self.clients_tree.bind("<Button-3>", self.show_context_menu)  # For Windows and Linux

        # Go Back Button
        go_back_button = ttk.Button(self, text="Go Back", command=go_back_callback)
        go_back_button.pack(pady=10)

    def show_context_menu(self, event):
        # Adjust to select the row under cursor
        row_id = self.clients_tree.identify_row(event.y)
        if row_id:
            self.clients_tree.selection_set(row_id)
            try:
                self.popup_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.popup_menu.grab_release()

    def open_add_client_form(self):
        """
        Opens the Add Client Form
        """
        AddClientForm(self.winfo_toplevel(), self.client_manager, self.load_clients_data)

    def load_clients_data(self):
        """
        Load and display clients data in the Treeview
        Using 'index' as the first column instead of the actual client_id
        """
        # Clear existing data in the tree
        for i in self.clients_tree.get_children():
            self.clients_tree.delete(i)

        # Fetch and insert new data
        clients = self.client_manager.get_all_clients()
        for index, client in enumerate(clients, start=1):
            client_id, *client_data = client
            self.clients_tree.insert('', 'end', values=(index, *client_data), tags=(client_id,))

    def open_edit_client_form(self):
        selected_items = self.clients_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a client to edit")
            return

        # Get the first selected item
        selected_item = selected_items[0]
        # Retrieve the client_id stored in the item's tag
        client_id = self.clients_tree.item(selected_item, 'tags')[0]
        client_id = int(client_id)
        EditClientForm(self.winfo_toplevel(), self.client_manager, client_id, self.load_clients_data)

    def trigger_delete_client(self):
        selected_items = self.clients_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a client to delete")
            return

        selected_item = selected_items[0]
        client_id = int(self.clients_tree.item(selected_item, 'tags')[0])

        # Check if client has transactions
        if self.client_manager.has_transactions(client_id):
            messagebox.showwarning("Warning", "Cannot delete client with existing transactions.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this client?"):
            self.client_manager.delete_client(client_id)
            self.load_clients_data()


class AddClientForm:
    def __init__(self, parent, client_manager, refresh_callback):
        self.window = tk.Toplevel(parent)
        self.window.title("Add New Client")
        self.window.geometry('300x300')

        self.client_manager = client_manager
        self.refresh_callback = refresh_callback

        # Form fields
        ttk.Label(self.window, text="Name(s):").pack(pady=(10, 0))
        self.name_entry = ttk.Entry(self.window)
        self.name_entry.pack()

        ttk.Label(self.window, text="Phone Number:").pack()
        self.phone_entry = ttk.Entry(self.window)
        self.phone_entry.pack()

        ttk.Label(self.window, text="Email:").pack()
        self.email_entry = ttk.Entry(self.window)
        self.email_entry.pack()

        ttk.Label(self.window, text="Notes:").pack()
        self.notes_entry = ttk.Entry(self.window)
        self.notes_entry.pack()

        submit_button = ttk.Button(self.window, text="Submit", command=self.submit)
        submit_button.pack(pady=10)

    def submit(self):
        """
        Method to handle the submission of the form
        """
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        notes = self.notes_entry.get()

        self.client_manager.add_client(name, phone, email, notes)
        self.refresh_callback()  # Refresh the clients list
        self.window.destroy()  # Close the form window


class EditClientForm:
    def __init__(self, parent, client_manager, client_id, refresh_callback):
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Client Details")
        self.window.geometry('300x300')

        self.client_manager = client_manager
        self.client_id = client_id
        self.refresh_callback = refresh_callback

        # Fetch client data
        client_data = self.client_manager.get_client(client_id)
        if client_data is None:
            messagebox.showerror("Error", "Client not found.")
            self.window.destroy()
            return

        _, name, phone, email, notes = client_data

        # Name field
        ttk.Label(self.window, text="Name:").pack(pady=(10, 0))
        self.name_entry = ttk.Entry(self.window)
        self.name_entry.insert(0, name)
        self.name_entry.pack()

        # Phone field
        ttk.Label(self.window, text="Phone Number:").pack()
        self.phone_entry = ttk.Entry(self.window)
        self.phone_entry.insert(0, phone)
        self.phone_entry.pack()

        # Email field
        ttk.Label(self.window, text="Email:").pack()
        self.email_entry = ttk.Entry(self.window)
        self.email_entry.insert(0, email)
        self.email_entry.pack()

        # Notes field
        ttk.Label(self.window, text="Notes:").pack()
        self.notes_entry = ttk.Entry(self.window)
        self.notes_entry.insert(0, notes)
        self.notes_entry.pack()

        submit_button = ttk.Button(self.window, text="Update", command=self.submit)
        submit_button.pack(pady=10)

    def submit(self):
        # Update client information
        updated_name = self.name_entry.get()
        updated_phone = self.phone_entry.get()
        updated_email = self.email_entry.get()
        updated_notes = self.notes_entry.get()

        self.client_manager.update_client(self.client_id, updated_name, updated_phone, updated_email, updated_notes)
        self.refresh_callback()  # Refresh the clients list
        self.window.destroy()  # Close the form window
