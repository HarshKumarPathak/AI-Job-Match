from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Recommendation
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
    return [
        _to_response(item)
        for item in _rank(db, candidate_id, limit, q, remote, location, employment_type, source)
    ]


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


@router.get("/{candidate_id}/history")
def recommendation_history(
    candidate_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    rows = db.scalars(
        select(Recommendation)
        .where(Recommendation.candidate_id == candidate_id)
        .order_by(Recommendation.created_at.desc())
        .limit(limit * 50)
    ).all()

    runs: list[dict] = []
    by_run: dict[str, dict] = {}

    for row in rows:
        run_id = row.run_id or f"legacy-{row.id}"
        run = by_run.get(run_id)
        if run is None:
            if len(runs) >= limit:
                continue
            run = {
                "run_id": run_id,
                "created_at": row.created_at,
                "recommendations": [],
            }
            by_run[run_id] = run
            runs.append(run)

        run["recommendations"].append(
            {
                "id": row.id,
                "job_id": row.job_id,
                "score": row.score,
                "matched_skills": [x.strip() for x in row.matched_skills.split(",") if x.strip()],
                "missing_skills": [x.strip() for x in row.missing_skills.split(",") if x.strip()],
            }
        )

    return runs
