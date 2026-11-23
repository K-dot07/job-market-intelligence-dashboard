from datetime import date
from fastapi import APIRouter, HTTPException, Query, FastAPI
from app.schemas.job import JobCreate

from app.services.job_service import (
    get_all_jobs,
    get_job_by_id,
    create_job,
    update_job,
    delete_job
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

@router.get("/")
def get_jobs(
    job_title: str | None = None,
    location: str | None = None,
    experience_level: str | None = None,
    skills: str | None = None,
    company: str | None = None,
    min_salary: float | None = None,
    max_salary: float | None = None,
    posted_from: date | None = None,
    posted_to: date | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort_by: str = "id",
    sort_order: str = "asc"
):
    if posted_from and posted_to:
        if posted_from > posted_to:
            raise HTTPException(
                status_code=400,
                detail="Start date cannot be later than end date"
            )
        
    if min_salary is not None and max_salary is not None:
        if min_salary > max_salary:
            raise HTTPException(
                status_code=400,
                detail="Minimum salary cannot be greater than maximum salary"
        )

    try:
        return get_all_jobs(
        job_title=job_title,
        location=location,
        experience_level=experience_level,
        skills=skills,
        company=company,
        min_salary=min_salary,
        max_salary=max_salary,
        posted_from=posted_from,
        posted_to=posted_to,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
    except ValueError as error:
        raise HTTPException(
        status_code=400,
        detail=str(error)
    )

@router.get("/{job_id}")
def get_job(job_id: int):
    job = get_job_by_id(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job

@router.post("/", status_code=201)
def create_new_job(job: JobCreate):
    new_id = create_job(job)

    return {
        "message": "Job created successfully",
        "job_id": new_id
    }

@router.put("/{job_id}")
def update_existing_job(job_id: int, job: JobCreate):
    updated_id = update_job(job_id, job)

    if updated_id is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return {
        "message": "Job updated successfully",
        "job_id": updated_id
    }

@router.delete("/{job_id}")
def delete_existing_job(job_id: int):
    deleted_id = delete_job(job_id)

    if deleted_id is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return {
        "message": "Job deleted successfully",
        "job_id": deleted_id
    }