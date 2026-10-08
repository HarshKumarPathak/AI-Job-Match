from app.domain.candidate import CandidateProfile
from app.domain.job import Job
from app.services.matching import explain_match


def test_matching_uses_skills_role_and_text() -> None:
    candidate = CandidateProfile(
        skills={"python", "sql"},
        preferred_roles={"AI Engineer"},
        resume_text="Python machine learning SQL data analysis",
    )
    job = Job(
        id="1",
        title="AI Engineer Intern",
        company="Example",
        description="Python machine learning and SQL work",
        skills={"python", "sql", "docker"},
    )

    result = explain_match(candidate, job)

    assert result.score > 60
    assert result.matched_skills == ("python", "sql")
    assert result.missing_skills == ("docker",)


def test_semantic_mode_uses_configured_service(monkeypatch) -> None:
    from app.config import settings
    from app.services import matching

    monkeypatch.setattr(settings, "matching_text_model", "semantic")
    monkeypatch.setattr("app.services.semantic_matching.similarity", lambda left, right: 0.8)

    candidate = CandidateProfile(resume_text="Python backend")
    job = Job(id="1", title="Backend", company="Test", description="API", skills=set())
    result = matching.explain_match(candidate, job)

    assert result.score == 16.0