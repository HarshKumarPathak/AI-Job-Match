from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Candidate, CandidateSkill, Job, JobSkill, Skill
from app.services.matching_db import match_candidate_to_job


def test_database_matching() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        candidate = Candidate(name="Test", preferred_roles="AI Engineer")
        python = Skill(name="python")
        sql = Skill(name="sql")
        docker = Skill(name="docker")
        db.add_all([candidate, python, sql, docker])
        db.flush()

        db.add_all([
            CandidateSkill(candidate_id=candidate.id, skill_id=python.id),
            CandidateSkill(candidate_id=candidate.id, skill_id=sql.id),
        ])

        job = Job(title="AI Engineer Intern", company="Example", description="")
        db.add(job)
        db.flush()
        db.add_all([
            JobSkill(job_id=job.id, skill_id=python.id),
            JobSkill(job_id=job.id, skill_id=sql.id),
            JobSkill(job_id=job.id, skill_id=docker.id),
        ])
        db.commit()

        result = match_candidate_to_job(db, candidate.id, job.id)

        assert result.matched_skills == ("python", "sql")
        assert result.missing_skills == ("docker",)
        assert result.score > 0
