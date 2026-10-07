from dataclasses import dataclass

from app.domain.candidate import CandidateProfile
from app.domain.job import Job as DomainJob
from app.services.matching import explain_match


@dataclass(frozen=True, slots=True)
class RecommendationView:
    job_id: int
    score: float
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]
    reasons: tuple[str, ...]


def build_recommendation(
    candidate_id: int,
    job_id: int,
    candidate: CandidateProfile,
    job: DomainJob,
) -> RecommendationView:
    result = explain_match(candidate, job)
    return RecommendationView(
        job_id=job_id,
        score=result.score,
        matched_skills=result.matched_skills,
        missing_skills=result.missing_skills,
        reasons=result.reasons,
    )
