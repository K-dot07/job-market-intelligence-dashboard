import pytest
from app.database.database import get_connection


@pytest.fixture
def test_db_connection(monkeypatch):
    monkeypatch.setenv("DB_NAME", "job_market_test_db")

    conn = get_connection()

    yield conn

    conn.close()