from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_api_test_job():
    return {
        "job_title": "Python Developer",
        "company_name": "Integration Test Company",
        "location": "Chennai",
        "experience_level": "Fresher",
        "skills": "Python, FastAPI",
        "salary": "3-5 LPA",
        "source_name": "Test Source"
    }

def test_api_create_job(test_db_connection):
    response = client.post(
        "/jobs/",
        json=create_api_test_job()
    )

    assert response.status_code == 201

    job_id = response.json()["job_id"]

    assert isinstance(job_id, int)

    client.delete(f"/jobs/{job_id}")

def test_api_get_job(test_db_connection):
    response = client.post(
        "/jobs/",
        json=create_api_test_job()
    )

    job_id = response.json()["job_id"]

    try:
        result = client.get(f"/jobs/{job_id}")

        assert result.status_code == 200
        assert result.json()["job_title"] == "Python Developer"

    finally:
        client.delete(f"/jobs/{job_id}")

def test_api_update_job(test_db_connection):
    response = client.post(
        "/jobs/",
        json=create_api_test_job()
    )

    job_id = response.json()["job_id"]

    updated_data = {
        **create_api_test_job(),
        "job_title": "Senior Python Developer",
        "company_name": "Updated Test Company"
    }

    try:
        result = client.put(
            f"/jobs/{job_id}",
            json=updated_data
        )

        assert result.status_code == 200

        updated = client.get(f"/jobs/{job_id}")

        assert updated.json()["job_title"] == "Senior Python Developer"

    finally:
        client.delete(f"/jobs/{job_id}")

def test_api_delete_job(test_db_connection):
    response = client.post(
        "/jobs/",
        json=create_api_test_job()
    )

    job_id = response.json()["job_id"]

    result = client.delete(f"/jobs/{job_id}")

    assert result.status_code == 200

    check = client.get(f"/jobs/{job_id}")

    assert check.status_code == 404

