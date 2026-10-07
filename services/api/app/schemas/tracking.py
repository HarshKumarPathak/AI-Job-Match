from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SavedJobCreate(BaseModel):
    candidate_id: int
    job_id: int


class SavedJobRead(SavedJobCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class ApplicationCreate(BaseModel):
    candidate_id: int
    job_id: int
    status: str = Field(default="applied", pattern="^(saved|applied|interview|rejected|offer)$")
    notes: str = ""


class ApplicationUpdate(BaseModel):
    status: str = Field(pattern="^(saved|applied|interview|rejected|offer)$")
    notes: str = ""


class ApplicationRead(ApplicationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    applied_at: datetime | None
    updated_at: datetime
