from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Job
from app.services.auth import get_current_user
from app.schemas.job import JobCreate, JobRead
from app.services.job_aggregator import ingest_source
from app.services.job_ingestion import save_job
from app.services.job_sources import DemoJobSource
from app.services.arbeitnow_source import ArbeitnowJobSource

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobRead, status_code=201)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> Job:
    job = save_job(db, payload.model_dump())
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
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
def ingest_demo_jobs(db: Session = Depends(get_db), _user=Depends(get_current_user)) -> dict[str, int]:
    count = ingest_source(db, DemoJobSource())
    db.commit()
    return {"source": "demo", "jobs_processed": count}


@router.post("/ingest/arbeitnow")
def ingest_arbeitnow_jobs(db: Session = Depends(get_db), _user=Depends(get_current_user)) -> dict[str, int]:
    count = ingest_source(db, ArbeitnowJobSource())
    db.commit()
    return {"source": "arbeitnow", "jobs_processed": count}
