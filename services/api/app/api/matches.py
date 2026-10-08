from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.auth import get_current_user, require_candidate_access
from app.schemas.match import MatchRead
from app.services.matching_db import match_candidate_to_job

router = APIRouter(prefix="/matches", tags=["matching"])


@router.get("/{candidate_id}/{job_id}", response_model=MatchRead)
def get_match(
    candidate_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
) -> MatchRead:
    require_candidate_access(candidate_id, user)
    try:
        result = match_candidate_to_job(db, candidate_id, job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return MatchRead(
        candidate_id=candidate_id,
        job_id=job_id,
        match_score=result.score,
        matched_skills=list(result.matched_skills),
        missing_skills=list(result.missing_skills),
        reasons=list(result.reasons),
    )
