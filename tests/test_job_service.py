import pytest
from unittest.mock import MagicMock
from app.services import job_service
from datetime import date
from app.schemas.job import JobCreate

def create_test_job():
    return JobCreate(
        job_title="Python Developer",
        company_name="ABC Technologies",
        location="Chennai",
        experience_level="Fresher",
        skills="Python, FastAPI, PostgreSQL",
        salary="3-5 LPA",
        source_name="Test Source",
        source_url=None,
        apply_url=None,
        posted_date=date(2026, 11, 23)
    )

def test_get_all_jobs_invalid_sort_by(monkeypatch):

    conn = MagicMock()

    monkeypatch.setattr(
        job_service,
        "get_connection",
        lambda: conn
    )

    with pytest.raises(ValueError, match="Invalid sorting column"):
        job_service.get_all_jobs(sort_by="wrong_column")

    conn.close.assert_called_once()

def test_get_all_jobs_invalid_sort_order(monkeypatch):

    conn = MagicMock()

    monkeypatch.setattr(
        job_service,
        "get_connection",
        lambda: conn
    )

    with pytest.raises(ValueError, match="Invalid sorting order"):
        job_service.get_all_jobs(sort_order="wrong")

    conn.close.assert_called_once()

def test_get_job_by_id_not_found(monkeypatch):

    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value.fetchone.return_value = None

    monkeypatch.setattr(
        job_service,
        "get_connection",
        lambda: conn
    )

    result = job_service.get_job_by_id(999)

    assert result is None
    conn.close.assert_called_once()

def test_get_job_by_id_success(monkeypatch):

    conn = MagicMock()

    fake_row = (
        10,
        "Python Developer",
        "TCS",
        "Chennai",
        "Fresher",
        "Python",
        "300000",
        "Adzuna",
        "https://example.com/job/10",
        "https://example.com/apply/10",
        None,
        None
    )

    conn.cursor.return_value.__enter__.return_value.fetchone.return_value = fake_row

    monkeypatch.setattr(
        job_service,
        "get_connection",
        lambda: conn
    )

    result = job_service.get_job_by_id(10)

    assert result["id"] == 10
    assert result["job_title"] == "Python Developer"
    assert result["company_name"] == "TCS"

    conn.close.assert_called_once()

def test_create_job(monkeypatch):

    conn = MagicMock()

    conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (25,)

    monkeypatch.setattr(
        job_service,
        "get_connection",
        lambda: conn
    )

    job = MagicMock()
    job.job_title = "Python Developer"
    job.company_name = "TCS"
    job.location = "Chennai"
    job.experience_level = "Fresher"
    job.skills = "Python"
    job.salary = "300000"
    job.source_name = "Adzuna"
    job.source_url = "https://example.com/job/25"
    job.apply_url = "https://example.com/apply/25"
    job.posted_date = None

    result = job_service.create_job(job)

    assert result == 25
    conn.commit.assert_called_once()
    conn.close.assert_called_once()


def test_update_job_success(monkeypatch):

    conn = MagicMock()

    conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (25,)

    monkeypatch.setattr(
        job_service,
        "get_connection",
        lambda: conn
    )

    job = MagicMock()
    job.job_title = "Python Developer"
    job.company_name = "Infosys"
    job.location = "Chennai"
    job.experience_level = "Fresher"
    job.skills = "Python"
    job.salary = "400000"
    job.source_name = "Adzuna"
    job.source_url = "https://example.com/job/25"
    job.apply_url = "https://example.com/apply/25"
    job.posted_date = None

    result = job_service.update_job(25, job)

    assert result == 25
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_update_job_not_found(monkeypatch):

    conn = MagicMock()

    conn.cursor.return_value.__enter__.return_value.fetchone.return_value = None

    monkeypatch.setattr(
        job_service,
        "get_connection",
        lambda: conn
    )

    job = MagicMock()

    result = job_service.update_job(999, job)

    assert result is None
    conn.commit.assert_not_called()
    conn.close.assert_called_once()

def test_delete_job_success(monkeypatch):

    conn = MagicMock()

    conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (25,)

    monkeypatch.setattr(
        job_service,
        "get_connection",
        lambda: conn
    )

    result = job_service.delete_job(25)

    assert result == 25
    conn.commit.assert_called_once()
    conn.close.assert_called_once()


def test_delete_job_not_found(monkeypatch):

    conn = MagicMock()

    conn.cursor.return_value.__enter__.return_value.fetchone.return_value = None

    monkeypatch.setattr(
        job_service,
        "get_connection",
        lambda: conn
    )

    result = job_service.delete_job(999)

    assert result is None
    conn.commit.assert_not_called()
    conn.close.assert_called_once()

def test_get_all_jobs_success(monkeypatch):

    conn = MagicMock()

    fake_row = (
        10,
        "Python Developer",
        "TCS",
        "Chennai",
        "Fresher",
        "Python",
        "300000",
        "Adzuna",
        "https://example.com/job/10",
        "https://example.com/apply/10",
        None,
        None
    )

    cursor = conn.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [fake_row]

    monkeypatch.setattr(
        job_service,
        "get_connection",
        lambda: conn
    )

    result = job_service.get_all_jobs()

    assert len(result) == 1
    assert result[0]["job_title"] == "Python Developer"
    assert result[0]["company_name"] == "TCS"

    conn.close.assert_called_once()

def setup_mock_db(monkeypatch, rows=None):

    conn = MagicMock()

    cursor = conn.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = rows or []

    monkeypatch.setattr(
        job_service,
        "get_connection",
        lambda: conn
    )

    return conn, cursor

def test_filter_by_job_title(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    job_service.get_all_jobs(job_title="Python")

    query, params = cursor.execute.call_args[0]

    assert "job_title ILIKE %s" in query
    assert "%Python%" in params
    conn.close.assert_called_once()

def test_filter_by_location(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    job_service.get_all_jobs(location="Chennai")

    query, params = cursor.execute.call_args[0]

    assert "location ILIKE %s" in query
    assert "%Chennai%" in params
    conn.close.assert_called_once()

def test_filter_by_salary(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    job_service.get_all_jobs(
        min_salary=300000,
        max_salary=800000
    )

    query, params = cursor.execute.call_args[0]

    assert "salary_min >= %s" in query
    assert "salary_max <= %s" in query
    assert 300000 in params
    assert 800000 in params
    conn.close.assert_called_once()

def test_filter_by_posted_date(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    job_service.get_all_jobs(
        posted_from="2026-11-01",
        posted_to="2026-11-20"
    )

    query, params = cursor.execute.call_args[0]

    assert "posted_date >= %s" in query
    assert "posted_date <= %s" in query
    assert "2026-11-01" in params
    assert "2026-11-20" in params
    conn.close.assert_called_once()

def test_combined_job_filters(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    job_service.get_all_jobs(
        job_title="Python",
        location="Chennai",
        company="TCS",
        min_salary=300000
    )

    query, params = cursor.execute.call_args[0]

    assert "job_title ILIKE %s" in query
    assert "location ILIKE %s" in query
    assert "company_name ILIKE %s" in query
    assert "salary_min >= %s" in query

    assert "%Python%" in params
    assert "%Chennai%" in params
    assert "%TCS%" in params
    assert 300000 in params

    conn.close.assert_called_once()

def test_filter_by_experience_level(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    job_service.get_all_jobs(experience_level="Fresher")

    query, params = cursor.execute.call_args[0]

    assert "experience_level ILIKE %s" in query
    assert "%Fresher%" in params
    conn.close.assert_called_once()


def test_filter_by_skills(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    job_service.get_all_jobs(skills="Python")

    query, params = cursor.execute.call_args[0]

    assert "skills ILIKE %s" in query
    assert "%Python%" in params
    conn.close.assert_called_once()


def test_filter_by_company(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    job_service.get_all_jobs(company="TCS")

    query, params = cursor.execute.call_args[0]

    assert "company_name ILIKE %s" in query
    assert "%TCS%" in params
    conn.close.assert_called_once()


def test_sort_by_posted_date(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    job_service.get_all_jobs(
        sort_by="posted_date",
        sort_order="desc"
    )

    query, params = cursor.execute.call_args[0]

    assert "ORDER BY posted_date desc" in query
    conn.close.assert_called_once()


def test_pagination(monkeypatch):
    conn, cursor = setup_mock_db(monkeypatch)

    job_service.get_all_jobs(limit=10, offset=20)

    query, params = cursor.execute.call_args[0]

    assert "LIMIT %s OFFSET %s" in query
    assert params[-2:] == (10, 20)
    conn.close.assert_called_once()

def test_create_job_with_postgres(test_db_connection):
    job = create_test_job()

    job_id = job_service.create_job(job)

    assert isinstance(job_id, int)
    assert job_id > 0

    job_service.delete_job(job_id)

def test_get_job_by_id_with_postgres(test_db_connection):
    job = create_test_job()
    job_id = job_service.create_job(job)

    try:
        result = job_service.get_job_by_id(job_id)

        assert result["id"] == job_id
        assert result["job_title"] == "Python Developer"
        assert result["company_name"] == "ABC Technologies"

    finally:
        job_service.delete_job(job_id)

def test_update_job_with_postgres(test_db_connection):
    job = create_test_job()
    job_id = job_service.create_job(job)

    updated_job = JobCreate(
        job_title="Senior Python Developer",
        company_name="XYZ Technologies",
        location="Bangalore",
        experience_level="Experienced"
    )

    try:
        result = job_service.update_job(job_id, updated_job)

        assert result == job_id

        updated = job_service.get_job_by_id(job_id)

        assert updated["job_title"] == "Senior Python Developer"
        assert updated["company_name"] == "XYZ Technologies"

    finally:
        job_service.delete_job(job_id)

def test_delete_job_with_postgres(test_db_connection):
    job = create_test_job()
    job_id = job_service.create_job(job)

    result = job_service.delete_job(job_id)

    assert result == job_id
    assert job_service.get_job_by_id(job_id) is None


def insert_test_jobs():
    job1 = create_test_job()
    job2 = JobCreate(
        job_title="Django Developer",
        company_name="XYZ Technologies",
        location="Bangalore",
        posted_date=date(2026, 11, 20)
    )

    id1 = job_service.create_job(job1)
    id2 = job_service.create_job(job2)

    return id1, id2

def test_get_all_jobs_with_postgres(test_db_connection):
    id1, id2 = insert_test_jobs()

    try:
        jobs = job_service.get_all_jobs()

        job_ids = [job["id"] for job in jobs]

        assert id1 in job_ids
        assert id2 in job_ids

    finally:
        job_service.delete_job(id1)
        job_service.delete_job(id2)

def test_filter_jobs_by_title_with_postgres(test_db_connection):
    id1, id2 = insert_test_jobs()

    try:
        jobs = job_service.get_all_jobs(job_title="Python")

        assert any(job["id"] == id1 for job in jobs)
        assert all("Python" in job["job_title"] for job in jobs)

    finally:
        job_service.delete_job(id1)
        job_service.delete_job(id2)

def test_filter_jobs_by_location_with_postgres(test_db_connection):
    id1, id2 = insert_test_jobs()

    try:
        jobs = job_service.get_all_jobs(location="Chennai")

        assert any(job["id"] == id1 for job in jobs)
        assert all(job["location"] == "Chennai" for job in jobs)

    finally:
        job_service.delete_job(id1)
        job_service.delete_job(id2)

def test_sort_jobs_by_posted_date_with_postgres(test_db_connection):
    id1, id2 = insert_test_jobs()

    try:
        jobs = job_service.get_all_jobs(
            sort_by="posted_date",
            sort_order="desc"
        )

        dates = [job["posted_date"] for job in jobs if job["id"] in (id1, id2)]

        assert dates == sorted(dates, reverse=True)

    finally:
        job_service.delete_job(id1)
        job_service.delete_job(id2)

