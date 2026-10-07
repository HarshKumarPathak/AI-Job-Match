from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Job
from app.schemas.job import JobCreate, JobRead
from app.services.job_ingestion import save_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobRead, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)) -> Job:
    job = save_job(db, payload.model_dump())
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[Job]:
    return list(db.scalars(select(Job).order_by(Job.created_at.desc())).all())
