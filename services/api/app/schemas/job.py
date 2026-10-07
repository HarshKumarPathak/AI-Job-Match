from pydantic import BaseModel


class JobRead(BaseModel):
    id: int
    title: str
    company: str
    description: str
    location: str | None = None
    remote: bool
    employment_type: str | None = None
    apply_url: str | None = None
    source: str | None = None
