from dataclasses import dataclass, field


@dataclass(slots=True)
class Job:
    id: str
    title: str
    company: str
    description: str
    skills: set[str] = field(default_factory=set)
    location: str | None = None
    remote: bool = False
    employment_type: str | None = None
    apply_url: str | None = None
    source: str | None = None
