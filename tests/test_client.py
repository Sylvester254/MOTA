import pytest
import sqlite3
from models import Client
from database import DatabaseManager


@pytest.fixture
def db_connection(tmpdir):
    """Fixture to create a temporary SQLite DB for each test"""
    db_file = tmpdir.join("test.db")
    conn = sqlite3.connect(str(db_file))  # str() conversion might be needed for PosixPath
    yield conn
    conn.close()


@pytest.fixture
def db_manager(db_connection):
    """Fixture using the DB connection to provide a DatabaseManager"""
    db_manager = DatabaseManager(str(db_connection.cursor().execute("PRAGMA foreign_keys").fetchone()[0]))
    yield db_manager
    db_manager.close_connection()


def test_add_client_success(db_manager):
    client = Client(name="Test Client", email="test@example.com")
    new_id = client.add_client(db_manager)

    assert new_id is not None  # First ensure an ID was actually generated

    # Fetch from the database for verification
    cursor = db_manager.execute_query("SELECT * FROM clients WHERE id=?", (new_id,))
    result = cursor.fetchone()
    assert result is not None
    assert result[1] == "Test Client"
    assert result[3] == "test@example.com"  # Check additional fields ...


def test_add_client_no_name(db_manager):
    client = Client(email="test@example.com")
    with pytest.raises(ValueError, match="Client name cannot be empty."):
        client.add_client(db_manager)

    # optionally verify that nothing was inserted in the database here


def test_add_client_invalid_email(db_manager):
    client = Client(name="Test Client", email="invalid_email")
    with pytest.raises(ValueError, match="Invalid email format."):
        client.add_client(db_manager)


def test_get_client(db_manager):
    # Pre-populate a client in the database for this test
    db_manager.execute_query("INSERT INTO clients(name, email) VALUES(?, ?)",
                             ("Test Client", "test@example.com"))

    result = Client.get_client(1, db_manager)
    assert result[0] == 1
    assert result[1] == "Test Client"
    assert result[3] == "test@example.com"
    # ... Other assertions ...


def test_get_all_clients(db_manager):
    clients = Client.get_all_clients(db_manager)
    assert len(clients) >= 0


def test_update_client_success(db_manager):
    # Pre-populate a client
    db_manager.execute_query("INSERT INTO clients(name, email) VALUES(?, ?)",
                             ("Old Name", "old@example.com"))
    client_id = db_manager.execute_query("SELECT last_insert_rowid()").fetchone()[0]

    client = Client(client_id=client_id, name="Updated Name", email="updated@example.com")
    client.update_client(db_manager)

    # Fetch from the database for verification
    cursor = db_manager.execute_query("SELECT * FROM clients WHERE id=?", (client_id,))
    result = cursor.fetchone()
    assert result[1] == "Updated Name"  # Check if name was updated


def test_update_client_no_id(db_manager):
    client = Client(name="Some Name", email="test@example.com")
    with pytest.raises(ValueError, match="Client ID is not set. Cannot update."):
        client.update_client(db_manager)


def test_has_transactions_true(db_manager):
    client_id = 1  # Assuming you control how IDs are assigned for setup
    # Setup: Insert at least a client and a related transaction

    assert Client.has_transactions(client_id, db_manager)


def test_has_transactions_false(db_manager):
    client_id = 2  # Use a different ID than in the previous test
    # Only setup the client - no related transaction on purpose

    assert not Client.has_transactions(client_id, db_manager)


def test_delete_client(db_manager):
    db_manager.execute_query("INSERT INTO clients(name, email) VALUES(?, ?)",
                             ("ToDelete", "delete@example.com"))
    client_id = db_manager.execute_query("SELECT last_insert_rowid()").fetchone()[0]

    Client.delete_client(client_id, db_manager)

    cursor = db_manager.execute_query("SELECT COUNT(*) FROM clients WHERE id=?", (client_id,))
    count = cursor.fetchone()[0]
    assert count == 0
