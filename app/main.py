from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from app.database.database import get_connection
from app.routers.jobs import router as jobs_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class QuoteCreate(BaseModel):
    text: str = Field(min_length=3)
    author: str = Field(min_length=2)

app = FastAPI(
    title="Job Market Dashboard API",
    description="Backend API for the Job Market Dashboard",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(jobs_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to Job Market Dashboard API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/quotes/{quote_id}")
def get_quote_by_id(quote_id: int):

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, text, author
                FROM quotes
                WHERE id = %s
                """,
                (quote_id,)
            )

            row = cursor.fetchone()

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Quote not found"
                )

            return {
                "id": row[0],
                "text": row[1],
                "author": row[2]
            }

    finally:
        conn.close()

 
@app.post("/quotes", status_code=201)
def create_quote(quote: QuoteCreate):

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO quotes (text, author)
                VALUES (%s, %s)
                RETURNING id, text, author
                """,
                (quote.text, quote.author)
            )

            row = cursor.fetchone()
            conn.commit()

            return {
                "id": row[0],
                "text": row[1],
                "author": row[2]
            }

    finally:
        conn.close()

@app.put("/quotes/{quote_id}")
def update_quote(quote_id: int, quote: QuoteCreate):

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE quotes
                SET text = %s, author = %s
                WHERE id = %s
                RETURNING id, text, author
                """,
                (quote.text, quote.author, quote_id)
            )

            row = cursor.fetchone()

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Quote not found"
                )

            conn.commit()

            return {
                "id": row[0],
                "text": row[1],
                "author": row[2]
            }

    finally:
        conn.close()

@app.delete("/quotes/{quote_id}")
def delete_quote(quote_id: int):

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM quotes
                WHERE id = %s
                RETURNING id
                """,
                (quote_id,)
            )

            row = cursor.fetchone()

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Quote not found"
                )

            conn.commit()

            return {
                "message": "Quote deleted successfully",
                "id": row[0]
            }

    finally:
        conn.close()
