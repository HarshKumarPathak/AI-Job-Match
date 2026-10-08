from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.auth import get_current_user, require_candidate_access
from app.models import Candidate, JobAlert
from app.schemas.alert import AlertMatchRead, JobAlertCreate, JobAlertRead, JobAlertUpdate
from app.services.alert_service import matching_alert_jobs

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=JobAlertRead, status_code=201)
def create_alert(payload: JobAlertCreate, db: Session = Depends(get_db), user = Depends(get_current_user)) -> JobAlert:
    require_candidate_access(payload.candidate_id, user)
    if db.get(Candidate, payload.candidate_id) is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    existing = db.scalar(
        select(JobAlert)
        .where(JobAlert.candidate_id == payload.candidate_id)
        .order_by(JobAlert.created_at.desc())
    )
    if existing:
        existing.minimum_score = payload.minimum_score
        existing.enabled = True
        db.commit()
        db.refresh(existing)
        return existing

    alert = JobAlert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/{candidate_id}", response_model=JobAlertRead | None)
def get_alert(candidate_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)) -> JobAlert | None:
    require_candidate_access(candidate_id, user)
    return db.scalar(
        select(JobAlert)
        .where(JobAlert.candidate_id == candidate_id)
        .order_by(JobAlert.created_at.desc())
    )


@router.patch("/{alert_id}", response_model=JobAlertRead)
def update_alert(
    alert_id: int,
    payload: JobAlertUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
) -> JobAlert:
    alert = db.get(JobAlert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    require_candidate_access(alert.candidate_id, user)

    alert.minimum_score = payload.minimum_score
    alert.enabled = payload.enabled
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/{candidate_id}/matches", response_model=list[AlertMatchRead])
def check_alert(candidate_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)) -> list[AlertMatchRead]:
    require_candidate_access(candidate_id, user)
    _alert, matches = matching_alert_jobs(db, candidate_id)
    return [
        AlertMatchRead(
            job_id=item.job.id,
            title=item.job.title,
            company=item.job.company,
            score=item.score,
            apply_url=item.job.apply_url,
        )
        for item in matches
    ]
