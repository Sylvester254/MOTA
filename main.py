from database import DatabaseConnection
from client import Client


def main():
    database_path = './mota.sqlite'

    # create a database connection
    db_connection = DatabaseConnection(database_path)

    # create instance of the Client class
    client_manager = Client(db_connection)

    new_client_id = 1

    # example adding new client
    # new_client_id = client_manager.add_client("Alice Smith", "123-456-7890", "alice@example.com", "Regular client")
    # print(f"Added new client with id: {new_client_id}")

    # example updating client's details
    # client_manager.update_client(new_client_id, "Alice Johnson", "123-456-7890", "alicej@example.com", "Updated info")
    # print(f"Updated client with ID: {new_client_id}")

    # # example deleting a client
    # client_manager.delete_client(new_client_id)
    # print(f"Deleted client with ID: {new_client_id}")

    # Example retrieving client's details
    client_details = client_manager.get_client(new_client_id)
    print(f"Client's Details: {client_details}")

    # close the db connection
    db_connection.close_connection()


if __name__ == '__main__':
    main()
