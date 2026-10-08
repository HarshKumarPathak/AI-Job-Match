"""Small explainable heuristics for turning resume text into profile hints."""

import re

EDUCATION_PATTERNS = (
    r"b\.?tech", r"bachelor", r"m\.?tech", r"master", r"bca", r"mca",
    r"bsc", r"msc", r"mba", r"phd",
)

ROLE_KEYWORDS = (
    "ai engineer", "ml engineer", "machine learning engineer", "data scientist",
    "data analyst", "backend developer", "software engineer", "full stack developer",
    "frontend developer", "python developer", "generative ai engineer",
)

def infer_profile(text: str) -> dict[str, object]:
    lowered = text.lower()
    education = None
    for pattern in EDUCATION_PATTERNS:
        match = re.search(pattern + r"[^\n]{0,80}", lowered)
        if match:
            education = match.group(0).strip()
            break

    roles = [role for role in ROLE_KEYWORDS if role in lowered]
    experience_years = 0.0
    match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)", lowered)
    if match:
        experience_years = float(match.group(1))

    return {
        "education": education,
        "preferred_roles": roles[:5],
        "experience_years": experience_years,
    }
