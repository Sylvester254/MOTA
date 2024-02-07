import tkinter as tk
from tkinter import ttk, messagebox, Tk
from client import ClientsPage
from database import DatabaseConnection
from transactions import TransactionsPage


class App:
    def __init__(self, root, db_connection):
        self.root = root
        self.db_connection = db_connection

        # Configure the style and apply a theme
        self.style = ttk.Style()
        # print(self.style.theme_names())
        self.style.theme_use('aqua')  # 'aqua', 'clam', 'alt', 'default', 'classic'

        # Main menu frame
        self.menu_frame = ttk.Frame(self.root)
        self.setup_main_menu()

        # Clients & Transactions frame
        self.clients_frame = ClientsPage(self.root, db_connection, self.show_main_menu)
        self.transactions_frame = TransactionsPage(self.root, db_connection, self.show_main_menu)

        # Positioning frames using place
        self.menu_frame.place(relwidth=1, relheight=1)
        self.clients_frame.place(relwidth=1, relheight=1)
        self.transactions_frame.place(relwidth=1, relheight=1)

        # Initially, only the main menu is visible
        self.menu_frame.lift()

    def setup_main_menu(self):
        welcome_label = ttk.Label(self.menu_frame, text="\n\tWelcome to MOTA!\n   Your Freelance Earnings Manager!", font=("Georgia", 20, "bold"))
        welcome_label.pack(pady=20)

        transactions_button = ttk.Button(self.menu_frame, text="Transactions", command=self.show_transactions)
        transactions_button.pack(pady=(5, 1))

        clients_button = ttk.Button(self.menu_frame, text="Clients", command=self.show_clients)
        clients_button.pack(pady=1)

        reports_button = ttk.Button(self.menu_frame, text="Analysis Reports", command=self.show_reports)
        reports_button.pack(pady=(1, 5))

    def show_main_menu(self):
        self.clients_frame.lower()
        self.menu_frame.lift()

    def show_clients(self):
        self.menu_frame.lower()
        self.clients_frame.lift()

    # Placeholder methods for transactions and reports
    def show_transactions(self):
        self.menu_frame.lower()
        self.transactions_frame.lift()

    def show_reports(self):
        messagebox.showinfo("Info", "Reports page under development")


def main():
    database_path = './mota.sqlite'
    db_connection = DatabaseConnection(database_path)

    root = tk.Tk()
    root.title("MOTA")
    root.geometry('1000x600')

    app = App(root, db_connection)
    root.mainloop()


if __name__ == '__main__':
    main()
