from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Job
from app.services.matching_db import match_candidate_to_job


@dataclass(frozen=True, slots=True)
class RankedRecommendation:
    job: Job
    score: float
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]
    reasons: tuple[str, ...]


def recommend_jobs(
    db: Session,
    candidate_id: int,
    limit: int = 10,
    q: str | None = None,
    remote: bool | None = None,
    location: str | None = None,
    employment_type: str | None = None,
    source: str | None = None,
) -> list[RankedRecommendation]:
    statement = select(Job)

    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            Job.title.ilike(pattern) | Job.company.ilike(pattern) | Job.description.ilike(pattern)
        )
    if remote is not None:
        statement = statement.where(Job.remote.is_(remote))
    if location:
        statement = statement.where(Job.location.ilike(f"%{location.strip()}%"))
    if employment_type:
        statement = statement.where(Job.employment_type.ilike(f"%{employment_type.strip()}%"))
    if source:
        statement = statement.where(Job.source.ilike(f"%{source.strip()}%"))

    jobs = db.scalars(statement).all()
    recommendations: list[RankedRecommendation] = []

    for job in jobs:
        try:
            result = match_candidate_to_job(db, candidate_id, job.id)
        except ValueError:
            continue

        recommendations.append(
            RankedRecommendation(
                job=job,
                score=result.score,
                matched_skills=result.matched_skills,
                missing_skills=result.missing_skills,
                reasons=result.reasons,
            )
        )

    recommendations.sort(key=lambda item: item.score, reverse=True)
    return recommendations[: max(1, limit)]
