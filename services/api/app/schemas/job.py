from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    external_id: str | None = None
    title: str
    company: str
    description: str = ""
    location: str | None = None
    remote: bool = False
    employment_type: str | None = None
    apply_url: str | None = None
    source: str | None = None
    skills: list[str] = Field(default_factory=list)


class JobRead(JobCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
