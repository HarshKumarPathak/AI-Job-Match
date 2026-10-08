from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Candidate
from app.schemas.candidate import CandidateCreate, CandidateRead
from app.services.auth import get_current_user, require_candidate_access

router = APIRouter(prefix="/candidates", tags=["candidates"])


def _to_read(candidate: Candidate) -> CandidateRead:
    return CandidateRead(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        preferred_roles=[item for item in candidate.preferred_roles.splitlines() if item.strip()],
        preferred_locations=[
            item for item in candidate.preferred_locations.splitlines() if item.strip()
        ],
        experience_years=candidate.experience_years,
        education=candidate.education,
    )


@router.post("", response_model=CandidateRead)
def create_candidate(
    payload: CandidateCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> CandidateRead:
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
    return _to_read(candidate)


@router.get("/{candidate_id}", response_model=CandidateRead)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> CandidateRead:
    require_candidate_access(candidate_id, user)
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return _to_read(candidate)
