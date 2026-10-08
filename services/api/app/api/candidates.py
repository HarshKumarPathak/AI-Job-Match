from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Candidate
from app.schemas.candidate import CandidateCreate, CandidateRead
from app.services.auth import get_current_user, require_candidate_access

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("", response_model=CandidateRead)
def create_candidate(
    payload: CandidateCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> Candidate:
    candidate = db.get(Candidate, user.candidate_id)
    if candidate is None:
        raise HTTPException(status_code=500, detail="Account profile is missing")

    require_candidate_access(candidate.id, user)
    candidate.name = payload.name
    candidate.email = user.email
    candidate.preferred_roles = "\n".join(payload.preferred_roles)
    candidate.preferred_locations = "\n".join(payload.preferred_locations)
    candidate.experience_years = payload.experience_years
    candidate.education = payload.education

    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/{candidate_id}", response_model=CandidateRead)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> Candidate:
    require_candidate_access(candidate_id, user)
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
