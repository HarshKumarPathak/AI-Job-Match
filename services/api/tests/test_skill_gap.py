from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Candidate, CandidateSkill, Job, JobSkill, Skill
from app.services.skill_gap import analyze_skill_gaps


def test_skill_gaps_prioritize_common_missing_skills() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        candidate = Candidate(name="Test")
        python = Skill(name="python")
        sql = Skill(name="sql")
        docker = Skill(name="docker")
        db.add_all([candidate, python, sql, docker])
        db.flush()

        db.add(CandidateSkill(candidate_id=candidate.id, skill_id=python.id))

        first_job = Job(title="Python Intern", company="A", description="")
        second_job = Job(title="Backend Intern", company="B", description="")
        db.add_all([first_job, second_job])
        db.flush()

        db.add_all([
            JobSkill(job_id=first_job.id, skill_id=python.id),
            JobSkill(job_id=first_job.id, skill_id=sql.id),
            JobSkill(job_id=first_job.id, skill_id=docker.id),
            JobSkill(job_id=second_job.id, skill_id=sql.id),
        ])
        db.commit()

        analyzed, gaps = analyze_skill_gaps(db, candidate.id, job_limit=2)

        assert analyzed == 2
        assert gaps[0]["skill"] == "sql"
        assert gaps[0]["jobs_requiring_skill"] == 2
        assert gaps[1]["skill"] == "docker"
