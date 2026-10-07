ALIASES = {
    "py": "python",
    "python3": "python",
    "postgres": "postgresql",
    "js": "javascript",
    "ts": "typescript",
    "ml": "machine learning",
    "ai": "artificial intelligence",
}


def normalize_skill(skill: str) -> str:
    cleaned = " ".join(skill.lower().strip().split())
    return ALIASES.get(cleaned, cleaned)


def normalize_skills(skills: list[str]) -> list[str]:
    return sorted({normalize_skill(skill) for skill in skills if skill.strip()})
