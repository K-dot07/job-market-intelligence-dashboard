from app.services.job_service import get_all_jobs


def test_service_import():
    assert callable(get_all_jobs)