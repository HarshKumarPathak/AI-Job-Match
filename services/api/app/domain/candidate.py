from dataclasses import dataclass, field


@dataclass(slots=True)
class CandidateProfile:
    skills: set[str] = field(default_factory=set)
    preferred_roles: set[str] = field(default_factory=set)
    preferred_locations: set[str] = field(default_factory=set)
    experience_years: float = 0.0
    education: str | None = None
