from fastapi import APIRouter

from app.domain.candidate import CandidateProfile
from app.domain.job import Job
from app.services.matching import explain_match

router = APIRouter(prefix="/api/v1")


@router.post("/match/preview")
def preview_match() -> dict:
    candidate = CandidateProfile(
        skills={"Python", "SQL", "Machine Learning"},
        preferred_roles={"AI Engineer"},
        preferred_locations={"Remote"},
    )
    job = Job(
        id="demo",
        title="AI Engineer Intern",
        company="Demo Company",
        description="Build ML systems.",
        skills={"Python", "SQL", "Machine Learning", "Docker"},
        location="Remote",
        remote=True,
    )
    result = explain_match(candidate, job)
    return {
        "match_score": result.score,
        "matched_skills": result.matched_skills,
        "missing_skills": result.missing_skills,
        "reasons": result.reasons,
    }
