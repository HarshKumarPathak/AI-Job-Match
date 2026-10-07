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
