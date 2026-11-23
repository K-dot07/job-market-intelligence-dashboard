from app.database.database import get_connection

def get_all_jobs(
    job_title=None,
    location=None,
    experience_level=None,
    skills=None,
    company=None,
    min_salary=None,
    max_salary=None,
    posted_from=None,
    posted_to=None,
    limit=10,
    offset=0,
    sort_by="id",
    sort_order="asc"
):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            query = """
                SELECT *
                FROM jobs
                WHERE 1=1
            """

            params = []

            if job_title:
                query += " AND job_title ILIKE %s"
                params.append(f"%{job_title}%")

            if min_salary is not None:
                query += " AND salary_min >= %s"
                params.append(min_salary)

            if max_salary is not None:
                query += " AND salary_max <= %s"
                params.append(max_salary)

            if location:
                query += " AND location ILIKE %s"
                params.append(f"%{location}%")

            if experience_level:
                query += " AND experience_level ILIKE %s"
                params.append(f"%{experience_level}%")

            if skills:
                query += " AND skills ILIKE %s"
                params.append(f"%{skills}%")

            if company:
                query += " AND company_name ILIKE %s"
                params.append(f"%{company}%")

            if posted_from:
                query += " AND posted_date >= %s"
                params.append(posted_from)

            if posted_to:
                query += " AND posted_date <= %s"
                params.append(posted_to)

            allowed_sort_columns = {
                "id": "id",
                "title": "job_title",
                "company": "company_name",
                "location": "location",
                "posted_date": "posted_date"
            }

            if sort_by not in allowed_sort_columns:
                raise ValueError("Invalid sorting column")

            column = allowed_sort_columns[sort_by]

            order = sort_order.lower()

            if order not in ["asc", "desc"]:
                raise ValueError("Invalid sorting order")

            query += f" ORDER BY {column} {order} LIMIT %s OFFSET %s"

            params.extend([limit, offset])


            cursor.execute(query, tuple(params))
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

def get_job_by_id(job_id: int):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM jobs
                WHERE id = %s
                """,
                (job_id,)
            )

            row = cursor.fetchone()

            if row is None:
                return None

            job = {
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

            return job

    finally:
        conn.close()


def create_job(job):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO jobs (
                    job_title,
                    company_name,
                    location,
                    experience_level,
                    skills,
                    salary,
                    source_name,
                    source_url,
                    apply_url,
                    posted_date
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    job.job_title,
                    job.company_name,
                    job.location,
                    job.experience_level,
                    job.skills,
                    job.salary,
                    job.source_name,
                    job.source_url,
                    job.apply_url,
                    job.posted_date
                )
            )

            new_id = cursor.fetchone()[0]

            conn.commit()

            return new_id

    finally:
        conn.close()

def update_job(job_id: int, job):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE jobs
                SET
                    job_title = %s,
                    company_name = %s,
                    location = %s,
                    experience_level = %s,
                    skills = %s,
                    salary = %s,
                    source_name = %s,
                    source_url = %s,
                    apply_url = %s,
                    posted_date = %s
                WHERE id = %s
                RETURNING id
                """,
                (
                    job.job_title,
                    job.company_name,
                    job.location,
                    job.experience_level,
                    job.skills,
                    job.salary,
                    job.source_name,
                    job.source_url,
                    job.apply_url,
                    job.posted_date,
                    job_id
                )
            )

            row = cursor.fetchone()

            if row is None:
                return None

            conn.commit()
            return row[0]

    finally:
        conn.close()

def delete_job(job_id: int):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM jobs
                WHERE id = %s
                RETURNING id
                """,
                (job_id,)
            )

            row = cursor.fetchone()

            if row is None:
                return None

            conn.commit()
            return row[0]

    finally:
        conn.close()