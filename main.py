import tkinter as tk
from tkinter import ttk, messagebox
from client import ClientsPage
from database import DatabaseConnection


def open_transactions():
    messagebox.showinfo("Info", "Transactions page here")


def open_clients(root, db_connection):
    # Function to open the Clients page
    ClientsPage(root, db_connection)


def open_reports():
    messagebox.showinfo("Info", "Reports page here")


def main():
    database_path = './mota.sqlite'

    # create a database connection
    db_connection = DatabaseConnection(database_path)

    # Set up the main window
    root = tk.Tk()
    root.title("Freelance Earnings Manager")
    root.geometry('600x400')

    # Welcome message
    welcome_message = "Welcome to Freelance Earnings Manager!\n Choose an option from the menu to get started."
    welcome_label = ttk.Label(root, text=welcome_message, font=("Arial", 12))
    welcome_label.pack(pady=20)

    # Menu buttons
    menu_frame = ttk.Frame(root)
    menu_frame.pack(pady=10)

    transactions_button = ttk.Button(menu_frame, text="View Transactions", command=open_transactions)
    transactions_button.pack(fill='x', expand=True)

    clients_button = ttk.Button(menu_frame, text="View Clients", command=lambda: open_clients(root, db_connection))
    clients_button.pack(fill='x', expand=True, pady=1)

    reports_button = ttk.Button(menu_frame, text="View Reports", command=open_reports)
    reports_button.pack(fill='x', expand=True)

    # Start the application
    root.mainloop()


if __name__ == '__main__':
    main()
