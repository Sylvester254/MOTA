# MOTA

> A desktop application for managing your freelance earnings.

- It focuses on displaying a high-level overview of your transactions (monthly totals) with the flexibility to drill down into more detailed views (daily transactions for a selected month). 
- This design will help in quickly assessing your earnings trends and accessing specific transaction details as needed.

## Design
### Database

1. **Clients Table**: Stores information about the clients.
   - Fields: Client ID (primary key), Name, Phone number (optional), Email (optional), Additional Notes (optional).

2. **Transactions Table**: Stores details of each transaction.
   - Fields: Transaction ID (primary key), Client ID (foreign key), Amount, Date of Transaction, Description (optional).

The relationship between Clients and Transactions is one-to-many: one client can have multiple transactions.

### User Interface Design

1. **Client Management Section**:
   - Add New Client: Form to enter client details.
   - View/Edit Clients: List of clients with options to edit or delete(right-click for options).
   - Delete a client (works only if client has no linked transactions)

2. **Transaction Management Section**:
   - A dropdown to select a year. 
   - A list to display month and monthly totals of selected year. 
   - Another list or detailed view to show daily transactions when a month is selected. 
   - Forms for adding or editing transactions(right-click transaction for Edit & Delete options).
   - Option to delete a transaction.
   


## File Structure and Contents

`mota/`

- **`database.py`**:
    - This file contains the `DatabaseConnection` class for handling the database connection and creating the tables.
- **`client.py`**:
    - Includes the `Client` class with methods for adding, retrieving, updating, and deleting client data.
    - Includes `ClientPage` class which is a subclass of main application window and has methods that now use tkinter for loading, 
  displaying and manipulating client data in database via the Clients class methods.
    - Has 'Go Back' button to navigate back to main menu.
- **`transaction.py`**:
    - Includes the `Transaction` class with methods for adding, retrieving, updating, and deleting transactions.
    - Includes `TransactionsPage` class similar to `ClientsPage`, using a frame to manage the layout, but in this case for transactions data.
    - Has 'Go Back' button to navigate back to main menu.
- **`main.py`**:
    - The entry point of the application, where I've integrated and used classes from other modules.
    - Handles the application logic, UI interactions, and uses classes from `client.py` and `transaction.py`.
    - Has `App` class which manages the main menu and the `ClientsPage` and `TransactionsPage` as frames within the same main window.
    - Displays the menu for navigating to the clients page and transactions page.


## User Guide
- To start and interact with the desktop app via tkinter UI:

1. Ensure Python is properly installed on your system 
2. Clone the repository locally: `git clone https://github.com/Sylvester254/MOTA`.
3. Change directory to `mota` directory and create a virtual environment: `python3 -m venv <env name here>`.
4. Activate the environment: `source <env name here>/bin/activate` (Mac/Linux) or `<env_name_here>\Scripts\activate` (Windows).
5. Run `python3 main.py` in your terminal.
That's it! this should open the Tkinter GUI.

- The sample data you'll see on the application exists in `finance_management.sqlite` database.
- If you'd like to create a new database, just delete `mota.sqlite`, then run `python3 database.py` and this will create a new empty database for your use.
