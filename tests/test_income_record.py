import pytest
import sqlite3
from models import IncomeRecord
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


MAX_TRANSACTION_AMOUNT = 10000  # For your validation logic


@pytest.fixture
def sample_income_record():
    return IncomeRecord(client_id=1, amount=200.0, date="2024-02-25", description="Project 1 payment")


def test_add_record_success(db_manager, sample_income_record):
    new_id = sample_income_record.add_record(db_manager)

    # Assertions using the database
    cursor = db_manager.execute_query("SELECT * FROM income_records WHERE id=?", (new_id,))
    record = cursor.fetchone()
    assert record is not None  # Basic verification it exists
    # ... More specific assertions on client_id, amount, etc.


def test_add_record_missing_client(db_manager):
    record = IncomeRecord(amount=100, date="2024-02-25")
    with pytest.raises(ValueError, match="Client is required."):
        record.add_record(db_manager)


def test_add_record_invalid_amount(db_manager, sample_income_record):
    sample_income_record.amount = -50  # Negative
    with pytest.raises(ValueError, match="Invalid amount."):
        sample_income_record.add_record(db_manager)

    sample_income_record.amount = MAX_TRANSACTION_AMOUNT + 1
    with pytest.raises(ValueError, match="Invalid amount."):
        sample_income_record.add_record(db_manager)


def test_add_record_invalid_date(db_manager, sample_income_record):
    sample_income_record.date = "invalid_format"
    with pytest.raises(ValueError, match="Invalid date format."):
        sample_income_record.add_record(db_manager)


def test_get_record_success(db_manager, income_id=1):
    cursor = db_manager.execute_query("SELECT * FROM income_records WHERE id=?", (income_id,))
    record = cursor.fetchone()
    assert record is not None


def test_update_record_success(db_manager):
    income_id = 1
    record = IncomeRecord(income_id=income_id, client_id=1, amount=1000.0, date="2024-02-25",
                          description="Project 1 payment")
    record.update_record(db_manager)

    cursor = db_manager.execute_query("SELECT * FROM income_records WHERE id=?", (income_id,))
    result = cursor.fetchone()
    assert result[2] == 1000.0


def test_delete_record(db_manager):
    income_id = 5
    IncomeRecord.delete_record(income_id, db_manager)

    cursor = db_manager.execute_query("SELECT * FROM income_records WHERE id=?", (income_id,))
    record = cursor.fetchone()
    assert record is None


def test_get_monthly_totals(db_manager):
    # Pre-populate income records spanning across different months:
    db_manager.execute_query("INSERT INTO income_records(client_id, amount, date) VALUES (1, 500.0, '2024-01-10')")
    db_manager.execute_query("INSERT INTO income_records(client_id, amount, date) VALUES (1, 250.0, '2024-01-25')")
    db_manager.execute_query("INSERT INTO income_records(client_id, amount, date) VALUES (1, 100.0, '2024-02-05')")
    db_manager.execute_query("INSERT INTO income_records(client_id, amount, date) VALUES (1, 300.0, '2024-02-12')")

    # Call the method to test
    monthly_totals = IncomeRecord.get_monthly_totals(2024, db_manager)

    # Assertions
    assert len(monthly_totals) == 2
    assert monthly_totals["01"] == 750.0
    assert monthly_totals["02"] == 400.0


def test_get_daily_records(db_manager):
    # Set up data - sample record in February
    db_manager.execute_query(
        "INSERT INTO income_records(client_id, amount, date, description) VALUES (1, 300.0, '2024-02-20', "
        "'Design work')")
    sample_record_id = db_manager.execute_query("SELECT last_insert_rowid()").fetchone()[0]

    # Additionally: set up record in a different month

    # Call the method
    daily_records = IncomeRecord.get_daily_records(2024, 2, db_manager)

    # Assertions
    assert "2024-02-20" in daily_records  # Ensure the date is a key
    assert len(daily_records["2024-02-20"]) == 1
    fetched_record = daily_records["2024-02-20"][0]
    assert fetched_record[0] == sample_record_id
    assert fetched_record[1] == 1
    assert fetched_record[2] == 300.0
    assert fetched_record[3] == 'Design work'
    assert fetched_record[4] == 'Test Client'
