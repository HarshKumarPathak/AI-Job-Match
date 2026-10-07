from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Candidate, CandidateSkill, Job, JobSkill, Skill
from app.services.recommendation_engine import recommend_jobs


def test_recommend_jobs_returns_highest_score_first() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        candidate = Candidate(name="Test")
        python = Skill(name="python")
        sql = Skill(name="sql")
        docker = Skill(name="docker")
        db.add_all([candidate, python, sql, docker])
        db.flush()

        db.add_all([
            CandidateSkill(candidate_id=candidate.id, skill_id=python.id),
            CandidateSkill(candidate_id=candidate.id, skill_id=sql.id),
        ])

        strong_job = Job(title="Python Intern", company="A", description="")
        weak_job = Job(title="DevOps Intern", company="B", description="")
        db.add_all([strong_job, weak_job])
        db.flush()

        db.add_all([
            JobSkill(job_id=strong_job.id, skill_id=python.id),
            JobSkill(job_id=strong_job.id, skill_id=sql.id),
            JobSkill(job_id=weak_job.id, skill_id=docker.id),
        ])
        db.commit()

        results = recommend_jobs(db, candidate.id, limit=2)

        assert len(results) == 2
        assert results[0].job.id == strong_job.id
        assert results[0].score > results[1].score
