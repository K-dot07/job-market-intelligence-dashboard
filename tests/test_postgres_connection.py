import pytest
import psycopg
from app.database import database



@pytest.mark.parametrize(
    "job_title, company_name",
    [
        (None, "ABC Technologies"),
        ("Python Developer", None),
    ]
)
def test_required_fields_constraint(
    test_db_connection,
    job_title,
    company_name
):
    conn = test_db_connection

    try:
        with conn.cursor() as cursor:
            with pytest.raises(psycopg.errors.NotNullViolation):
                cursor.execute("""
                    INSERT INTO jobs (job_title, company_name)
                    VALUES (%s, %s)
                """, (job_title, company_name))

    finally:
        conn.rollback()

def test_duplicate_job_prevention(test_db_connection):
    conn = test_db_connection

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO jobs (job_title, company_name, source_url)
                VALUES (%s, %s, %s)
            """, (
                "Python Developer",
                "ABC Technologies",
                "https://example.com/duplicate-test"
            ))

            with pytest.raises(psycopg.errors.UniqueViolation):
                cursor.execute("""
                    INSERT INTO jobs (job_title, company_name, source_url)
                    VALUES (%s, %s, %s)
                """, (
                    "Python Developer",
                    "ABC Technologies",
                    "https://example.com/duplicate-test"
                ))

    finally:
        conn.rollback()



def test_connection_uses_test_database(test_db_connection):
    with test_db_connection.cursor() as cursor:
        cursor.execute("SELECT current_database()")
        database_name = cursor.fetchone()[0]

    assert database_name == "job_market_test_db"

def test_insert_and_retrieve_job(test_db_connection):
    with test_db_connection.cursor() as cursor:

        # Create a temporary table
        cursor.execute("""
            CREATE TEMP TABLE test_jobs (
                id SERIAL PRIMARY KEY,
                job_title VARCHAR(150),
                company_name VARCHAR(150)
            )
        """)

        # Insert a job
        cursor.execute("""
            INSERT INTO test_jobs (job_title, company_name)
            VALUES (%s, %s)
            RETURNING id
        """, ("Python Developer", "ABC Technologies"))

        job_id = cursor.fetchone()[0]

        # Retrieve the job
        cursor.execute("""
            SELECT job_title, company_name
            FROM test_jobs
            WHERE id = %s
        """, (job_id,))

        job = cursor.fetchone()

    assert job == ("Python Developer", "ABC Technologies")

def test_insert_and_retrieve_actual_job(test_db_connection):
    conn = test_db_connection

    try:
        with conn.cursor() as cursor:
            # INSERT a job
            cursor.execute("""
                INSERT INTO jobs (
                    job_title,
                    company_name,
                    location,
                    source_url
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (
                "Python Developer",
                "ABC Technologies",
                "Chennai",
                "https://example.com/test-job-001"
            ))

            job_id = cursor.fetchone()[0]

            # SELECT the inserted job
            cursor.execute("""
                SELECT job_title, company_name, location
                FROM jobs
                WHERE id = %s
            """, (job_id,))

            job = cursor.fetchone()

        assert job == (
            "Python Developer",
            "ABC Technologies",
            "Chennai"
        )

    finally:
        # Undo test data
        conn.rollback()

def test_update_job(test_db_connection):
    conn = test_db_connection

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO jobs (job_title, company_name)
                VALUES (%s, %s)
                RETURNING id
            """, ("Python Developer", "ABC Technologies"))

            job_id = cursor.fetchone()[0]

            cursor.execute("""
                UPDATE jobs
                SET company_name = %s
                WHERE id = %s
            """, ("XYZ Technologies", job_id))

            cursor.execute("""
                SELECT company_name
                FROM jobs
                WHERE id = %s
            """, (job_id,))

            company = cursor.fetchone()[0]

        assert company == "XYZ Technologies"

    finally:
        conn.rollback()

def test_delete_job(test_db_connection):
    conn = test_db_connection

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO jobs (job_title, company_name)
                VALUES (%s, %s)
                RETURNING id
            """, ("Python Developer", "ABC Technologies"))

            job_id = cursor.fetchone()[0]

            cursor.execute("""
                DELETE FROM jobs
                WHERE id = %s
            """, (job_id,))

            cursor.execute("""
                SELECT * FROM jobs
                WHERE id = %s
            """, (job_id,))

            job = cursor.fetchone()

        assert job is None

    finally:
        conn.rollback()

def test_database_rollback(test_db_connection):
    conn = test_db_connection

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO jobs (job_title, company_name)
                VALUES (%s, %s)
                RETURNING id
            """, ("Rollback Developer", "Test Company"))

            job_id = cursor.fetchone()[0]

            conn.rollback()

            cursor.execute("""
                SELECT * FROM jobs WHERE id = %s
            """, (job_id,))

            job = cursor.fetchone()

        assert job is None

    finally:
        conn.rollback()


def test_database_connection_failure(monkeypatch):

    def mock_connection_error(**kwargs):
        raise psycopg.OperationalError("Database unavailable")

    monkeypatch.setattr(
        database.psycopg,
        "connect",
        mock_connection_error
    )

    with pytest.raises(psycopg.OperationalError):
        database.get_connection()