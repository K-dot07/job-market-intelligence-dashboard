from fastapi.testclient import TestClient
from app.main import app
from app.routers import jobs as jobs_router

client = TestClient(app)

def test_limit_above_maximum():
    response = client.get("/jobs?limit=150")

    assert response.status_code == 422


def test_negative_offset():
    response = client.get("/jobs?offset=-1")

    assert response.status_code == 422


def test_invalid_date_format():
    response = client.get(
        "/jobs?posted_from=invalid-date"
    )

    assert response.status_code == 422


def test_invalid_date_range():
    response = client.get(
        "/jobs?posted_from=2026-11-13&posted_to=2026-11-01"
    )

    assert response.status_code == 400

def test_create_job(monkeypatch):
    monkeypatch.setattr(
        jobs_router,
        "create_job",
        lambda job: 101
    )

    response = client.post(
        "/jobs/",
        json={
            "job_title": "Python Developer",
            "company_name": "TCS",
            "location": "Chennai"
        }
    )

    assert response.status_code == 201
    assert response.json()["job_id"] == 101

def test_update_job(monkeypatch):
    monkeypatch.setattr(
        jobs_router,
        "update_job",
        lambda job_id, job: job_id
    )

    response = client.put(
        "/jobs/101",
        json={
            "job_title": "Backend Developer",
            "company_name": "Infosys",
            "location": "Chennai"
        }
    )

    assert response.status_code == 200
    assert response.json()["job_id"] == 101

def test_update_job_not_found(monkeypatch):
    monkeypatch.setattr(
        jobs_router,
        "update_job",
        lambda job_id, job: None
    )

    response = client.put(
        "/jobs/999",
        json={
            "job_title": "Backend Developer",
            "company_name": "Infosys"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

def test_delete_job(monkeypatch):
    monkeypatch.setattr(
        jobs_router,
        "delete_job",
        lambda job_id: job_id
    )

    response = client.delete("/jobs/101")

    assert response.status_code == 200
    assert response.json()["job_id"] == 101

def test_delete_job_not_found(monkeypatch):
    monkeypatch.setattr(
        jobs_router,
        "delete_job",
        lambda job_id: None
    )

    response = client.delete("/jobs/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

def test_get_job_by_id(monkeypatch):
    fake_job = {
        "id": 101,
        "job_title": "Python Developer",
        "company_name": "TCS",
        "location": "Chennai"
    }

    monkeypatch.setattr(
        jobs_router,
        "get_job_by_id",
        lambda job_id: fake_job
    )

    response = client.get("/jobs/101")

    assert response.status_code == 200
    assert response.json()["job_title"] == "Python Developer"

def test_get_job_by_id_not_found(monkeypatch):
    monkeypatch.setattr(
        jobs_router,
        "get_job_by_id",
        lambda job_id: None
    )

    response = client.get("/jobs/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

def test_get_jobs_success(monkeypatch):
    fake_jobs = [
        {
            "id": 1,
            "job_title": "Python Developer",
            "company_name": "TCS"
        }
    ]

    monkeypatch.setattr(
        jobs_router,
        "get_all_jobs",
        lambda **kwargs: fake_jobs
    )

    response = client.get("/jobs/?location=Chennai")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["job_title"] == "Python Developer"

def test_invalid_salary_range():
    response = client.get(
        "/jobs/?min_salary=800000&max_salary=300000"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Minimum salary cannot be greater than maximum salary"
    )

def test_get_jobs_invalid_sort(monkeypatch):
    def mock_get_all_jobs(**kwargs):
        raise ValueError("Invalid sorting column")

    monkeypatch.setattr(
        jobs_router,
        "get_all_jobs",
        mock_get_all_jobs
    )

    response = client.get("/jobs/?sort_by=invalid")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid sorting column"

