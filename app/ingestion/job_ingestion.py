from app.database.database import get_connection
import logging
import os
from dotenv import load_dotenv
import requests


def fetch_jobs_from_api():
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 5,
        "what": "Python Developer",
        "where": "Chennai"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    print("Status code:", response.status_code)

    response.raise_for_status()

    data = response.json()

    print("Total results:", data.get("count", 0))

    return data

def transform_job(job):
    return {
        "job_title": job.get("title"),
        "company_name": job.get("company", {}).get("display_name"),
        "location": job.get("location", {}).get("display_name"),
        "source_name": "Adzuna",
        "source_url": job.get("redirect_url"),
        "apply_url": job.get("redirect_url"),
        "salary": (
                f"{job.get('salary_min')} - {job.get('salary_max')}"
                if job.get("salary_min") and job.get("salary_max")
                else None
            ),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "posted_date": job.get("created", "")[:10] or None
    }

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

logging.basicConfig(
    filename="logs/ingestion.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.info("Job ingestion started")
logger.warning("Duplicate job skipped")
logger.error("Test error message")

def get_sample_jobs():
    jobs = [
        {
            "job_title": "Python Developer",
            "company_name": "TCS",
            "location": "Chennai",
            "source_url": "https://example.com/job/101"
        },
        {
            "job_title": "Backend Developer",
            "company_name": "Infosys",
            "location": "Bangalore",
            "source_url": "https://example.com/job/102"
        },
        {
        "job_title": "Django Developer",
        "company_name": "Wipro",
        "location": "Chennai",
        "source_url": "https://example.com/job/103"
        }
    ]

    return jobs

def collect_jobs():
    jobs = get_sample_jobs()

    print(f"Collected {len(jobs)} jobs")

    return jobs

def clean_jobs(jobs):
    cleaned_jobs = []
    seen = set()

    for job in jobs:
        title = job.get("job_title", "").strip().lower()
        company = job.get("company_name", "").strip().lower()

        if not title or not company:
            continue

        unique_key = (title, company)

        if unique_key in seen:
            continue

        seen.add(unique_key)
        cleaned_jobs.append(job)

    return cleaned_jobs

def validate_jobs(jobs):
    valid_jobs = []

    for job in jobs:
        title = job.get("job_title", "").strip()
        company = job.get("company_name", "").strip()
        source_url = job.get("source_url", "").strip()

        if not title or not company or not source_url:
            continue

        valid_jobs.append(job)

    return valid_jobs

def save_jobs_to_db(jobs):
    conn = get_connection()
    inserted_count = 0

    try:
        with conn.cursor() as cursor:
            for job in jobs:
                cursor.execute(
                    """
                    INSERT INTO jobs (
                        job_title,
                        company_name,
                        location,
                        source_url,
                        source_name,
                        apply_url,
                        salary,
                        salary_min,
                        salary_max,
                        posted_date
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_url) WHERE source_url IS NOT NULL
                    DO NOTHING
                    """,
                    (
                        job["job_title"],
                        job["company_name"],
                        job.get("location"),
                        job.get("source_url"),
                        job.get("source_name"),
                        job.get("apply_url"),
                        job.get("salary"),
                        job.get("salary_min"),
                        job.get("salary_max"),
                        job.get("posted_date")
                    )
                )

                if cursor.rowcount == 1:
                    inserted_count += 1

        conn.commit()
        logger.info("Inserted %s jobs", inserted_count)

        return inserted_count

    except Exception:
        conn.rollback()
        logger.exception("Database insertion failed")
        raise

    finally:
        conn.close()

def update_existing_jobs(jobs):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            for job in jobs:
                cursor.execute(
                    """
                    UPDATE jobs
                    SET
                        source_name = %s,
                        apply_url = %s,
                        salary = %s,
                        salary_min = %s,
                        salary_max = %s,
                        posted_date = %s
                    WHERE source_url = %s
                    """,
                    (
                        job.get("source_name"),
                        job.get("apply_url"),
                        job.get("salary"),
                        job.get("salary_min"),
                        job.get("salary_max"),
                        job.get("posted_date"),
                        job.get("source_url")
                    )
                )

        conn.commit()
        logger.info("Existing jobs updated successfully")

    except Exception:
        conn.rollback()
        logger.exception("Job update failed")
        raise

    finally:
        conn.close()

def main():
    data = fetch_jobs_from_api()

    formatted_jobs = [
        transform_job(job)
        for job in data["results"]
    ]

    cleaned_jobs = clean_jobs(formatted_jobs)

    valid_jobs = validate_jobs(cleaned_jobs)

    inserted = save_jobs_to_db(valid_jobs)

    update_existing_jobs(valid_jobs)

    print("Total fetched:", len(formatted_jobs))
    print("Total valid:", len(valid_jobs))
    print("Total inserted:", inserted)


if __name__ == "__main__":
    main()