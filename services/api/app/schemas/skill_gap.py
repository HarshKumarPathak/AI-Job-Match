from pydantic import BaseModel


class SkillGapRead(BaseModel):
    skill: str
    priority: int
    jobs_requiring_skill: int
    reason: str


class SkillGapSummary(BaseModel):
    candidate_id: int
    analyzed_jobs: int
    gaps: list[SkillGapRead]
