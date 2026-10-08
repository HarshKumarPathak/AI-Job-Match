from uuid import uuid4
from sqlalchemy.orm import Session

from app.models import Recommendation
from app.services.recommendation_engine import RankedRecommendation


def persist_recommendations(
    db: Session,
    candidate_id: int,
    recommendations: list[RankedRecommendation],
) -> int:
    """Replace the candidate's latest recommendation snapshot."""
    run_id = str(uuid4())

    for item in recommendations:
        db.add(
            Recommendation(
                candidate_id=candidate_id,
                job_id=item.job.id,
                score=item.score,
                matched_skills=", ".join(item.matched_skills),
                missing_skills=", ".join(item.missing_skills),
                reasons=" | ".join(item.reasons),
                run_id=run_id,
            )
        )

    db.commit()
    return len(recommendations)
