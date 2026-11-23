
from datetime import date
from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    job_title: str = Field(min_length=2, max_length=150)
    company_name: str = Field(min_length=2, max_length=150)
    location: str | None = None
    experience_level: str | None = None
    skills: str | None = None
    salary: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    apply_url: str | None = None
    posted_date: date | None = None
