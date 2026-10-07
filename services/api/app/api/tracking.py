from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Application, Candidate, Job, SavedJob
from app.schemas.tracking import ApplicationCreate, ApplicationRead, ApplicationUpdate, SavedJobCreate, SavedJobRead

router = APIRouter(prefix="/tracking", tags=["tracking"])


def _check_candidate_job(db: Session, candidate_id: int, job_id: int) -> None:
    if db.get(Candidate, candidate_id) is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if db.get(Job, job_id) is None:
        raise HTTPException(status_code=404, detail="Job not found")


@router.post("/saved", response_model=SavedJobRead, status_code=201)
def save_job_for_candidate(payload: SavedJobCreate, db: Session = Depends(get_db)) -> SavedJob:
    _check_candidate_job(db, payload.candidate_id, payload.job_id)
    existing = db.scalar(select(SavedJob).where(
        SavedJob.candidate_id == payload.candidate_id,
        SavedJob.job_id == payload.job_id,
    ))
    if existing:
        return existing
    item = SavedJob(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/saved/{candidate_id}", response_model=list[SavedJobRead])
def list_saved_jobs(candidate_id: int, db: Session = Depends(get_db)) -> list[SavedJob]:
    return list(db.scalars(
        select(SavedJob).where(SavedJob.candidate_id == candidate_id).order_by(SavedJob.created_at.desc())
    ).all())


@router.post("/applications", response_model=ApplicationRead, status_code=201)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)) -> Application:
    _check_candidate_job(db, payload.candidate_id, payload.job_id)
    existing = db.scalar(select(Application).where(
        Application.candidate_id == payload.candidate_id,
        Application.job_id == payload.job_id,
    ))
    if existing:
        existing.status = payload.status
        existing.notes = payload.notes
        if payload.status == "applied" and existing.applied_at is None:
            existing.applied_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    item = Application(**payload.model_dump())
    if payload.status == "applied":
        item.applied_at = datetime.utcnow()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/applications/{candidate_id}", response_model=list[ApplicationRead])
def list_applications(candidate_id: int, db: Session = Depends(get_db)) -> list[Application]:
    return list(db.scalars(
        select(Application).where(Application.candidate_id == candidate_id).order_by(Application.updated_at.desc())
    ).all())


@router.patch("/applications/{application_id}", response_model=ApplicationRead)
def update_application(application_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)) -> Application:
    item = db.get(Application, application_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Application not found")
    item.status = payload.status
    item.notes = payload.notes
    if payload.status == "applied" and item.applied_at is None:
        item.applied_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item
