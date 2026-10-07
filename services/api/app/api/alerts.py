from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Candidate, JobAlert
from app.schemas.alert import AlertMatchRead, JobAlertCreate, JobAlertRead
from app.services.recommendation_engine import recommend_jobs

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=JobAlertRead, status_code=201)
def create_alert(payload: JobAlertCreate, db: Session = Depends(get_db)) -> JobAlert:
    if db.get(Candidate, payload.candidate_id) is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    alert = JobAlert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/{candidate_id}/matches", response_model=list[AlertMatchRead])
def check_alert(candidate_id: int, db: Session = Depends(get_db)) -> list[AlertMatchRead]:
    alert = db.scalar(select(JobAlert).where(
        JobAlert.candidate_id == candidate_id,
        JobAlert.enabled.is_(True),
    ).order_by(JobAlert.created_at.desc()))
    if alert is None:
        return []

    return [
        AlertMatchRead(
            job_id=item.job.id,
            title=item.job.title,
            company=item.job.company,
            score=item.score,
            apply_url=item.job.apply_url,
        )
        for item in recommend_jobs(db, candidate_id, 50)
        if item.score >= alert.minimum_score
    ]
