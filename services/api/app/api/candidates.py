from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Candidate
from app.schemas.candidate import CandidateCreate, CandidateRead

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("", response_model=CandidateRead, status_code=201)
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)) -> Candidate:
    candidate = Candidate(
        name=payload.name,
        email=payload.email,
        preferred_roles="\n".join(payload.preferred_roles),
        preferred_locations="\n".join(payload.preferred_locations),
        experience_years=payload.experience_years,
        education=payload.education,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate
