from pydantic import BaseModel


class RecommendationRead(BaseModel):
    job_id: int
    title: str
    company: str
    location: str | None
    remote: bool
    employment_type: str | None
    source: str | None
    apply_url: str | None
    salary_min: float | None
    salary_max: float | None
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    reasons: list[str]
