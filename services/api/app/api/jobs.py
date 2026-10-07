from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Job
from app.schemas.job import JobCreate, JobRead
from app.services.job_aggregator import ingest_source
from app.services.job_ingestion import save_job
from app.services.job_sources import DemoJobSource

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobRead, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)) -> Job:
    job = save_job(db, payload.model_dump())
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[JobRead])
def list_jobs(
    q: str | None = Query(default=None, min_length=1),
    remote: bool | None = None,
    location: str | None = None,
    employment_type: str | None = None,
    source: str | None = None,
    db: Session = Depends(get_db),
) -> list[Job]:
    statement = select(Job)

    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            Job.title.ilike(pattern) | Job.company.ilike(pattern) | Job.description.ilike(pattern)
        )
    if remote is not None:
        statement = statement.where(Job.remote.is_(remote))
    if location:
        statement = statement.where(Job.location.ilike(f"%{location.strip()}%"))
    if employment_type:
        statement = statement.where(Job.employment_type.ilike(f"%{employment_type.strip()}%"))
    if source:
        statement = statement.where(Job.source.ilike(f"%{source.strip()}%"))

    return list(db.scalars(statement.order_by(Job.created_at.desc())).all())


@router.post("/ingest/demo")
def ingest_demo_jobs(db: Session = Depends(get_db)) -> dict[str, int]:
    count = ingest_source(db, DemoJobSource())
    db.commit()
    return {"source": "demo", "jobs_processed": count}
