from pydantic import BaseModel


class MatchRead(BaseModel):
    candidate_id: int
    job_id: int
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    reasons: list[str]
