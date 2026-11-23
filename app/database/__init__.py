
from app.database.database import get_connection


def get_all_jobs():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT *
                FROM jobs
                ORDER BY id
            """)

            rows = cursor.fetchall()

            jobs = [
                {
                    "id": row[0],
                    "job_title": row[1],
                    "company_name": row[2],
                    "location": row[3],
                    "experience_level": row[4],
                    "skills": row[5],
                    "salary": row[6],
                    "source_name": row[7],
                    "source_url": row[8],
                    "apply_url": row[9],
                    "posted_date": row[10],
                    "created_at": row[11]
                }
                for row in rows
            ]

            return jobs

    finally:
        conn.close()
