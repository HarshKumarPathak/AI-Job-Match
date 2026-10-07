from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.skill_gap import SkillGapRead, SkillGapSummary
from app.services.skill_gap import analyze_skill_gaps

router = APIRouter(prefix="/skill-gaps", tags=["skill-gaps"])


@router.get("/{candidate_id}", response_model=SkillGapSummary)
def get_skill_gaps(
    candidate_id: int,
    job_limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> SkillGapSummary:
    try:
        analyzed_jobs, gaps = analyze_skill_gaps(db, candidate_id, job_limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return SkillGapSummary(
        candidate_id=candidate_id,
        analyzed_jobs=analyzed_jobs,
        gaps=[SkillGapRead(**gap) for gap in gaps],
    )
