from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobAlertCreate(BaseModel):
    candidate_id: int
    minimum_score: float = Field(default=70.0, ge=0, le=100)


class JobAlertUpdate(BaseModel):
    minimum_score: float = Field(default=70.0, ge=0, le=100)
    enabled: bool = True


class JobAlertRead(JobAlertCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    enabled: bool
    created_at: datetime


class AlertMatchRead(BaseModel):
    job_id: int
    title: str
    company: str
    score: float
    apply_url: str | None
