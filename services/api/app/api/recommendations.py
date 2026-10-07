from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.recommendation import RecommendationRead
from app.services.recommendation_engine import recommend_jobs

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{candidate_id}", response_model=list[RecommendationRead])
def get_recommendations(
    candidate_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[RecommendationRead]:
    try:
        recommendations = recommend_jobs(db, candidate_id, limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return [
        RecommendationRead(
            job_id=item.job.id,
            title=item.job.title,
            company=item.job.company,
            location=item.job.location,
            remote=item.job.remote,
            employment_type=item.job.employment_type,
            apply_url=item.job.apply_url,
            match_score=item.score,
            matched_skills=list(item.matched_skills),
            missing_skills=list(item.missing_skills),
            reasons=list(item.reasons),
        )
        for item in recommendations
    ]
