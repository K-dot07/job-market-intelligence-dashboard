import os
import psycopg
from dotenv import load_dotenv


load_dotenv()

def get_connection():
    
    conn = psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    return conn


def insert_quotes(quotes):

    # Empty data check:
    if not quotes:
        print("No quotes available.")
        return 0

    quote_data = [
        (quote["text"], quote["author"])
        for quote in quotes
    ]

    conn = None

    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO quotes (text, author)
                VALUES (%s, %s)
                ON CONFLICT (text, author) DO NOTHING
                """,
                quote_data
            )

            inserted_count = cursor.rowcount

        conn.commit()

        return inserted_count

    except Exception:
        if conn is not None:
            conn.rollback()

        raise

    finally:
        if conn is not None:
            conn.close()
