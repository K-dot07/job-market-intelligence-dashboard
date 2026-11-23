from unittest.mock import MagicMock
import pytest
import requests

from app.ingestion import job_ingestion

def setup_mock_db(monkeypatch):
    conn = MagicMock()
    cursor = conn.cursor.return_value.__enter__.return_value

    monkeypatch.setattr(
        job_ingestion,
        "get_connection",
        lambda: conn
    )

    return conn, cursor

def test_transform_job():
    job = {
        "title": "Python Developer",
        "company": {"display_name": "TCS"},
        "location": {"display_name": "Chennai"},
        "redirect_url": "https://example.com/job/1",
        "salary_min": 300000,
        "salary_max": 500000,
        "created": "2026-11-20T10:00:00Z"
    }

    result = job_ingestion.transform_job(job)

    assert result["job_title"] == "Python Developer"
    assert result["company_name"] == "TCS"
    assert result["location"] == "Chennai"
    assert result["salary"] == "300000 - 500000"
    assert result["posted_date"] == "2026-11-20"

def test_clean_jobs_removes_duplicates():
    jobs = [
        {
            "job_title": "Python Developer",
            "company_name": "TCS"
        },
        {
            "job_title": "Python Developer",
            "company_name": "TCS"
        },
        {
            "job_title": "Backend Developer",
            "company_name": "Infosys"
        }
    ]

    result = job_ingestion.clean_jobs(jobs)

    assert len(result) == 2

def test_clean_jobs_removes_invalid_jobs():
    jobs = [
        {
            "job_title": "Python Developer",
            "company_name": "TCS"
        },
        {
            "job_title": "",
            "company_name": "Infosys"
        },
        {
            "job_title": "Backend Developer",
            "company_name": ""
        }
    ]

    result = job_ingestion.clean_jobs(jobs)

    assert len(result) == 1
    assert result[0]["company_name"] == "TCS"

def test_validate_jobs():
    jobs = [
        {
            "job_title": "Python Developer",
            "company_name": "TCS",
            "source_url": "https://example.com/1"
        },
        {
            "job_title": "",
            "company_name": "Infosys",
            "source_url": "https://example.com/2"
        },
        {
            "job_title": "Backend Developer",
            "company_name": "Wipro",
            "source_url": ""
        }
    ]

    result = job_ingestion.validate_jobs(jobs)

    assert len(result) == 1
    assert result[0]["job_title"] == "Python Developer"

def test_save_jobs_to_db(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)
    cursor.rowcount = 1

    jobs = [
        {
            "job_title": "Python Developer",
            "company_name": "TCS",
            "location": "Chennai",
            "source_url": "https://example.com/1"
        }
    ]

    result = job_ingestion.save_jobs_to_db(jobs)

    assert result == 1
    conn.commit.assert_called_once()
    conn.close.assert_called_once()


def test_save_jobs_to_db_rollback(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)
    cursor.execute.side_effect = Exception("Database error")

    jobs = [
        {
            "job_title": "Python Developer",
            "company_name": "TCS",
            "source_url": "https://example.com/1"
        }
    ]

    with pytest.raises(Exception, match="Database error"):
        job_ingestion.save_jobs_to_db(jobs)

    conn.rollback.assert_called_once()
    conn.close.assert_called_once()

def test_fetch_jobs_from_api(monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "count": 1,
        "results": [{"title": "Python Developer"}]
    }

    mock_get = MagicMock(return_value=mock_response)
    monkeypatch.setattr(job_ingestion.requests, "get", mock_get)

    result = job_ingestion.fetch_jobs_from_api()

    assert result["count"] == 1
    assert len(result["results"]) == 1
    mock_get.assert_called_once()
    mock_response.raise_for_status.assert_called_once()

def test_fetch_jobs_from_api_failure(monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.HTTPError(
        "API error"
    )

    monkeypatch.setattr(
        job_ingestion.requests,
        "get",
        MagicMock(return_value=mock_response)
    )

    with pytest.raises(requests.HTTPError):
        job_ingestion.fetch_jobs_from_api()

def test_update_existing_jobs(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    jobs = [
        {
            "source_name": "Adzuna",
            "apply_url": "https://example.com/apply/1",
            "salary": "300000 - 500000",
            "salary_min": 300000,
            "salary_max": 500000,
            "posted_date": "2026-11-20",
            "source_url": "https://example.com/job/1"
        }
    ]

    job_ingestion.update_existing_jobs(jobs)

    cursor.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_update_existing_jobs_rollback(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)
    cursor.execute.side_effect = Exception("Update failed")

    jobs = [
        {
            "source_url": "https://example.com/job/1"
        }
    ]

    with pytest.raises(Exception, match="Update failed"):
        job_ingestion.update_existing_jobs(jobs)

    conn.rollback.assert_called_once()
    conn.close.assert_called_once()

def test_get_sample_jobs():
    result = job_ingestion.get_sample_jobs()

    assert len(result) == 3
    assert result[0]["job_title"] == "Python Developer"
    assert result[1]["company_name"] == "Infosys"

def test_collect_jobs(monkeypatch):
    sample_jobs = [
        {"job_title": "Python Developer"},
        {"job_title": "Backend Developer"}
    ]

    monkeypatch.setattr(
        job_ingestion,
        "get_sample_jobs",
        lambda: sample_jobs
    )

    result = job_ingestion.collect_jobs()

    assert len(result) == 2
    assert result == sample_jobs

def test_clean_jobs_case_insensitive_duplicates():
    jobs = [
        {
            "job_title": "Python Developer",
            "company_name": "TCS"
        },
        {
            "job_title": "PYTHON DEVELOPER",
            "company_name": "tcs"
        }
    ]

    result = job_ingestion.clean_jobs(jobs)

    assert len(result) == 1

def test_transform_job_without_salary_and_date():
    job = {
        "title": "Backend Developer",
        "company": {"display_name": "Infosys"},
        "location": {"display_name": "Chennai"},
        "redirect_url": "https://example.com/job/2"
    }

    result = job_ingestion.transform_job(job)

    assert result["salary"] is None
    assert result["salary_min"] is None
    assert result["salary_max"] is None
    assert result["posted_date"] is None

def test_save_jobs_to_db_duplicate(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    cursor.rowcount = 0

    jobs = [
        {
            "job_title": "Python Developer",
            "company_name": "TCS",
            "source_url": "https://example.com/job/1"
        }
    ]

    result = job_ingestion.save_jobs_to_db(jobs)

    assert result == 0
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_main_pipeline(monkeypatch, capsys):
    sample_api_data = {
        "results": [
            {"title": "Python Developer"},
            {"title": "Backend Developer"}
        ]
    }

    monkeypatch.setattr(
        job_ingestion,
        "fetch_jobs_from_api",
        lambda: sample_api_data
    )

    monkeypatch.setattr(
        job_ingestion,
        "transform_job",
        lambda job: {
            "job_title": job["title"],
            "company_name": "TCS",
            "source_url": "https://example.com/job/1"
        }
    )

    monkeypatch.setattr(
        job_ingestion,
        "save_jobs_to_db",
        lambda jobs: 2
    )

    monkeypatch.setattr(
        job_ingestion,
        "update_existing_jobs",
        lambda jobs: None
    )

    job_ingestion.main()

    output = capsys.readouterr().out

    assert "Total fetched: 2" in output
    assert "Total valid: 2" in output
    assert "Total inserted: 2" in output

def test_main_pipeline_empty_results(monkeypatch, capsys):
    monkeypatch.setattr(
        job_ingestion,
        "fetch_jobs_from_api",
        lambda: {"results": []}
    )

    monkeypatch.setattr(
        job_ingestion,
        "save_jobs_to_db",
        lambda jobs: 0
    )

    monkeypatch.setattr(
        job_ingestion,
        "update_existing_jobs",
        lambda jobs: None
    )

    job_ingestion.main()

    output = capsys.readouterr().out

    assert "Total fetched: 0" in output
    assert "Total valid: 0" in output
    assert "Total inserted: 0" in output