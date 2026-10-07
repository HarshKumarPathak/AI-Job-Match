import re

from app.services.skill_normalization import normalize_skill


KNOWN_SKILLS = {
    "python", "sql", "java", "javascript", "typescript", "c++",
    "machine learning", "deep learning", "artificial intelligence",
    "generative ai", "nlp", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "fastapi", "django", "flask", "react",
    "next.js", "node.js", "postgresql", "mongodb", "docker", "git", "github",
}


def extract_skills(text: str) -> list[str]:
    normalized_text = re.sub(r"\s+", " ", text.lower())
    found = []
    for skill in KNOWN_SKILLS:
        if re.search(r"(?<![a-z0-9+#.-])" + re.escape(skill) + r"(?![a-z0-9+#.-])", normalized_text):
            found.append(normalize_skill(skill))
    return sorted(set(found))
