from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.recommendation import RecommendationRead
from app.services.recommendation_engine import recommend_jobs
from app.services.recommendation_persistence import persist_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def _to_response(item) -> RecommendationRead:
    return RecommendationRead(
        job_id=item.job.id,
        title=item.job.title,
        company=item.job.company,
        location=item.job.location,
        remote=item.job.remote,
        employment_type=item.job.employment_type,
        source=item.job.source,
        apply_url=item.job.apply_url,
        match_score=item.score,
        matched_skills=list(item.matched_skills),
        missing_skills=list(item.missing_skills),
        reasons=list(item.reasons),
    )


def _rank(
    db: Session,
    candidate_id: int,
    limit: int,
    q: str | None,
    remote: bool | None,
    location: str | None,
    employment_type: str | None,
    source: str | None,
):
    try:
        return recommend_jobs(
            db,
            candidate_id,
            limit,
            q=q,
            remote=remote,
            location=location,
            employment_type=employment_type,
            source=source,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{candidate_id}", response_model=list[RecommendationRead])
def get_recommendations(
    candidate_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    q: str | None = Query(default=None, min_length=1),
    remote: bool | None = None,
    location: str | None = None,
    employment_type: str | None = None,
    source: str | None = None,
    db: Session = Depends(get_db),
) -> list[RecommendationRead]:
    return [_to_response(item) for item in _rank(
        db, candidate_id, limit, q, remote, location, employment_type, source
    )]


@router.post("/{candidate_id}/refresh", response_model=list[RecommendationRead])
def refresh_recommendations(
    candidate_id: int,
    limit: int = Query(default=20, ge=1, le=50),
    q: str | None = Query(default=None, min_length=1),
    remote: bool | None = None,
    location: str | None = None,
    employment_type: str | None = None,
    source: str | None = None,
    db: Session = Depends(get_db),
) -> list[RecommendationRead]:
    recommendations = _rank(
        db, candidate_id, limit, q, remote, location, employment_type, source
    )
    persist_recommendations(db, candidate_id, recommendations)
    return [_to_response(item) for item in recommendations]
