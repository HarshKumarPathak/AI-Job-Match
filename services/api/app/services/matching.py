from dataclasses import dataclass

from app.domain.candidate import CandidateProfile
from app.domain.job import Job


@dataclass(frozen=True, slots=True)
class MatchResult:
    score: float
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]
    reasons: tuple[str, ...]


def _normalize(values: set[str]) -> set[str]:
    return {value.strip().lower() for value in values if value.strip()}


def explain_match(candidate: CandidateProfile, job: Job) -> MatchResult:
    candidate_skills = _normalize(candidate.skills)
    job_skills = _normalize(job.skills)

    matched = sorted(candidate_skills & job_skills)
    missing = sorted(job_skills - candidate_skills)

    skill_score = len(matched) / len(job_skills) if job_skills else 0.0

    role_score = 0.0
    if candidate.preferred_roles:
        title = job.title.lower()
        role_score = max(
            (1.0 if role.lower() in title else 0.0)
            for role in candidate.preferred_roles
        )

    location_score = 0.0
    if candidate.preferred_locations and job.location:
        location_score = max(
            (1.0 if location.lower() in job.location.lower() else 0.0)
            for location in candidate.preferred_locations
        )

    score = round((skill_score * 0.70 + role_score * 0.20 + location_score * 0.10) * 100, 2)

    reasons = []
    if matched:
        reasons.append(f"{len(matched)} required skills matched")
    if role_score:
        reasons.append("Preferred role appears in the job title")
    if location_score:
        reasons.append("Preferred location matches")
    if missing:
        reasons.append(f"{len(missing)} skills need improvement")

    return MatchResult(
        score=score,
        matched_skills=tuple(matched),
        missing_skills=tuple(missing),
        reasons=tuple(reasons),
    )
