import datetime

from database import DatabaseConnection
from client import Client
from transactions import Transaction


def main():
    database_path = './finance_management.sqlite'

    # create a database connection
    db_connection = DatabaseConnection(database_path)

    # create instance of the Client and Transaction classes
    client_manager = Client(db_connection)
    transaction_manager = Transaction(db_connection)

    new_client_id = 12

    # example adding new client
    # new_client_id = client_manager.add_client("Jon Doe", "123-456-7890", "jd@example.com", "new client")
    # print(f"Added new client with id: {new_client_id}")

    # example updating client's details
    # client_manager.update_client(new_client_id, "Alice Johnson", "123-456-7890", "alicej@example.com", "Updated info")
    # print(f"Updated client with ID: {new_client_id}")

    # example deleting a client
    # client_manager.delete_client(new_client_id)
    # print(f"Deleted client with ID: {new_client_id}")

    # Example retrieving client's details
    client_details = client_manager.get_client(new_client_id)
    print(f"Client's Details: {client_details}")

    # Example: Adding a new transaction
    client_id = new_client_id
    amount = 4000.00
    date = '2024-01-27'
    description = "scripts"
    # new_transaction_id = transaction_manager.add_transaction(client_id, amount, date, description)
    # print(f"Added new transaction with ID: {new_transaction_id}")

    new_transaction_id = 26

    # # Example: Updating a transaction's details
    # updated_amount = 5500.00
    # updated_description = "Project Payment - Final"
    # transaction_manager.update_transaction(new_transaction_id, client_id, updated_amount, date, updated_description)
    # print(f"Updated transaction with ID: {new_transaction_id}")
    #
    # # Example: Deleting a transaction
    # transaction_manager.delete_transaction(new_transaction_id)
    # print(f"Deleted transaction with ID: {new_transaction_id}")

    # Example: Retrieving a transaction's details
    transaction_details = transaction_manager.get_transaction(new_transaction_id)
    print(f"Transaction Details: {transaction_details}")

    # close the db connection
    db_connection.close_connection()


if __name__ == '__main__':
    main()

# (26, 1, -2000.0, '20220205', 'data validation')
# (25, 1, -2000.0, '20240203', 'validation test')

# (12, '', '', '', '')
