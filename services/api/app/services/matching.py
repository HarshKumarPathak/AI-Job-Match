from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings

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


def _text_similarity(candidate_text: str, job_text: str) -> float:
    if not candidate_text.strip() or not job_text.strip():
        return 0.0
    if settings.matching_text_model.lower() == "semantic":
        from app.services.semantic_matching import similarity
        return similarity(candidate_text, job_text)
    matrix = TfidfVectorizer(stop_words="english").fit_transform([candidate_text, job_text])
    return float(cosine_similarity(matrix[0:1], matrix[1:2])[0, 0])


def explain_match(candidate: CandidateProfile, job: Job) -> MatchResult:
    candidate_skills = _normalize(candidate.skills)
    job_skills = _normalize(job.skills)

    matched = sorted(candidate_skills & job_skills)
    missing = sorted(job_skills - candidate_skills)

    skill_score = len(matched) / len(job_skills) if job_skills else 0.0
    text_score = _text_similarity(
        candidate.resume_text,
        f"{job.title} {job.description}",
    )

    role_score = 0.0
    if candidate.preferred_roles:
        title = job.title.lower()
        role_score = max(1.0 if role.lower() in title else 0.0 for role in candidate.preferred_roles)

    location_score = 0.0
    if candidate.preferred_locations and job.location:
        location_score = max(
            1.0 if location.lower() in job.location.lower() else 0.0
            for location in candidate.preferred_locations
        )

    experience_score = 0.0
    if job.experience_min_years is not None or job.experience_max_years is not None:
        minimum = job.experience_min_years if job.experience_min_years is not None else 0.0
        maximum = job.experience_max_years
        if candidate.experience_years >= minimum and (maximum is None or candidate.experience_years <= maximum):
            experience_score = 1.0
        elif candidate.experience_years < minimum and minimum > 0:
            experience_score = max(0.0, candidate.experience_years / minimum)
        else:
            experience_score = 0.5
    else:
        experience_score = 1.0

    score = round(
        (skill_score * 0.50 + text_score * 0.20 + role_score * 0.15 + location_score * 0.10 + experience_score * 0.05) * 100,
        2,
    )

    reasons = []
    if matched:
        reasons.append(f"{len(matched)} required skills matched")
    if text_score >= 0.25:
        reasons.append("Resume content is similar to the job description")
    if role_score:
        reasons.append("Preferred role appears in the job title")
    if location_score:
        reasons.append("Preferred location matches")
    if experience_score == 1.0 and (job.experience_min_years is not None or job.experience_max_years is not None):
        reasons.append("Experience level fits the role")
    elif experience_score < 1.0 and (job.experience_min_years is not None or job.experience_max_years is not None):
        reasons.append("Experience level is a partial fit")
    if missing:
        reasons.append(f"{len(missing)} skills need improvement")

    return MatchResult(
        score=score,
        matched_skills=tuple(matched),
        missing_skills=tuple(missing),
        reasons=tuple(reasons),
    )
