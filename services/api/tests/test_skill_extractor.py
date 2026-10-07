from app.services.skill_extractor import extract_skills


def test_extract_skills_finds_known_skills() -> None:
    text = "Built projects with Python, SQL, FastAPI and machine learning."
    assert extract_skills(text) == ["fastapi", "machine learning", "python", "sql"]
