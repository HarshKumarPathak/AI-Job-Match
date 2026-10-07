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
) -> list[RankedRecommendation]:
    jobs = db.scalars(select(Job)).all()
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
