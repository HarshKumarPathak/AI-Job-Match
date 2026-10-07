from app.domain.candidate import CandidateProfile
from app.domain.job import Job
from app.services.matching import explain_match


def test_matching_explains_skill_gap() -> None:
    candidate = CandidateProfile(skills={"Python", "SQL"})
    job = Job(
        id="1",
        title="ML Intern",
        company="Example",
        description="",
        skills={"Python", "SQL", "Docker"},
    )

    result = explain_match(candidate, job)

    assert result.score > 0
    assert result.matched_skills == ("python", "sql")
    assert result.missing_skills == ("docker",)
