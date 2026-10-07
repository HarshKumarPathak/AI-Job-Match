from pydantic import BaseModel, Field


class CandidateCreate(BaseModel):
    name: str | None = None
    email: str | None = None
    preferred_roles: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    experience_years: float = Field(default=0.0, ge=0)
    education: str | None = None


class CandidateRead(CandidateCreate):
    id: int
