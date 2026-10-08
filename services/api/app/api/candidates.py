from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.auth import get_current_user, require_candidate_access
from app.models import Candidate
from app.schemas.candidate import CandidateCreate, CandidateRead

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("", response_model=CandidateRead, status_code=201)
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db), user = Depends(get_current_user)) -> Candidate:
    candidate = (
        db.scalar(select(Candidate).where(Candidate.email == payload.email))
        if payload.email
        else None
    )

    if candidate is None:
        candidate = Candidate()
        db.add(candidate)

    if candidate is not None:
        require_candidate_access(candidate.id, user)
    candidate.name = payload.name
    candidate.email = payload.email
    candidate.preferred_roles = "\n".join(payload.preferred_roles)
    candidate.preferred_locations = "\n".join(payload.preferred_locations)
    candidate.experience_years = payload.experience_years
    candidate.education = payload.education

    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/{candidate_id}", response_model=CandidateRead)
def get_candidate(candidate_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if candidate is not None:
        require_candidate_access(candidate_id, user)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
