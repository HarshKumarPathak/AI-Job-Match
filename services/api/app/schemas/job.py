from pydantic import BaseModel, ConfigDict


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    description: str
    location: str | None = None
    remote: bool
    employment_type: str | None = None
    apply_url: str | None = None
    source: str | None = None
