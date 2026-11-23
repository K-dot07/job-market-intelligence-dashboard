from unittest.mock import MagicMock, patch
import pytest
from app.database import database


def test_insert_quotes_closes_connection_on_error():
    mock_conn = MagicMock()

    with patch.object(
        database,
        "get_connection",
        return_value=mock_conn
    ):
        mock_conn.cursor.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            database.insert_quotes([
                {
                    "text": "Test quote",
                    "author": "Test author"
                }
            ])

    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()

def test_insert_quotes_empty():
    result = database.insert_quotes([])

    assert result == 0


def test_insert_quotes_success(monkeypatch):

    # Create a fake database connection
    fake_conn = MagicMock()

    # Configure fake cursor
    fake_cursor = fake_conn.cursor.return_value.__enter__.return_value
    fake_cursor.rowcount = 2

    # Replace the real connection function
    monkeypatch.setattr(
    database,
    "get_connection",
    lambda: fake_conn
)

    # Sample data
    quotes = [
        {"text": "Quote one", "author": "Author one"},
        {"text": "Quote two", "author": "Author two"}
    ]

    # Execute the function
    result = database.insert_quotes(quotes)

    # Verify results
    assert result == 2
    fake_cursor.executemany.assert_called_once()
    fake_conn.commit.assert_called_once()
    fake_conn.close.assert_called_once()

def test_get_connection(monkeypatch):
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "job_market_db")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "test_password")

    mock_conn = MagicMock()

    monkeypatch.setattr(
        database.psycopg,
        "connect",
        lambda **kwargs: mock_conn
    )

    result = database.get_connection()

    assert result == mock_conn

def test_insert_quotes_empty():
    result = database.insert_quotes([])

    assert result == 0

def test_insert_quotes_success(monkeypatch):
    conn = MagicMock()
    cursor = conn.cursor.return_value.__enter__.return_value
    cursor.rowcount = 2

    monkeypatch.setattr(
        database,
        "get_connection",
        lambda: conn
    )

    quotes = [
        {"text": "Learn Python", "author": "John"},
        {"text": "Practice coding", "author": "David"}
    ]

    result = database.insert_quotes(quotes)

    assert result == 2
    cursor.executemany.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_insert_quotes_rollback(monkeypatch):
    conn = MagicMock()
    cursor = conn.cursor.return_value.__enter__.return_value

    cursor.executemany.side_effect = Exception("Database error")

    monkeypatch.setattr(
        database,
        "get_connection",
        lambda: conn
    )

    quotes = [
        {"text": "Learn Python", "author": "John"}
    ]

    with pytest.raises(Exception, match="Database error"):
        database.insert_quotes(quotes)

    conn.rollback.assert_called_once()
    conn.close.assert_called_once()