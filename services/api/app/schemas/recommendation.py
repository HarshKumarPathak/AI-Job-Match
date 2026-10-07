from pydantic import BaseModel


class RecommendationRead(BaseModel):
    job_id: int
    title: str
    company: str
    location: str | None
    remote: bool
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    reasons: list[str]
