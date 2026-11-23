from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app import main

client = TestClient(app)


def setup_mock_db(monkeypatch):
    conn = MagicMock()
    cursor = conn.cursor.return_value.__enter__.return_value

    monkeypatch.setattr(
        main,
        "get_connection",
        lambda: conn
    )

    return conn, cursor

def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Welcome to Job Market Dashboard API"
    )


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_quote_by_id(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    cursor.fetchone.return_value = (
        1, "Learning Python", "John"
    )

    response = client.get("/quotes/1")

    assert response.status_code == 200
    assert response.json()["text"] == "Learning Python"
    assert response.json()["author"] == "John"
    conn.close.assert_called_once()

def test_create_quote(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    cursor.fetchone.return_value = (
        1, "Learning Python", "John"
    )

    response = client.post(
        "/quotes",
        json={
            "text": "Learning Python",
            "author": "John"
        }
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_update_quote(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    cursor.fetchone.return_value = (
        1, "Python is powerful", "John"
    )

    response = client.put(
        "/quotes/1",
        json={
            "text": "Python is powerful",
            "author": "John"
        }
    )

    assert response.status_code == 200
    assert response.json()["text"] == "Python is powerful"
    conn.commit.assert_called_once()
    conn.close.assert_called_once()


def test_update_quote_not_found(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)
    cursor.fetchone.return_value = None

    response = client.put(
        "/quotes/999",
        json={
            "text": "Python is powerful",
            "author": "John"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Quote not found"
    conn.close.assert_called_once()


def test_delete_quote(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)
    cursor.fetchone.return_value = (1,)

    response = client.delete("/quotes/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1
    conn.commit.assert_called_once()
    conn.close.assert_called_once()


def test_delete_quote_not_found(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)
    cursor.fetchone.return_value = None

    response = client.delete("/quotes/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Quote not found"
    conn.close.assert_called_once()

def test_get_quote_not_found(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)
    cursor.fetchone.return_value = None

    response = client.get("/quotes/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Quote not found"
    conn.close.assert_called_once()


