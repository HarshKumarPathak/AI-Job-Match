from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Candidate, CandidateSkill, Job, Resume, Skill
from app.services.job_ingestion import save_job
from app.services.recommendation_engine import recommend_jobs


def test_recommendations_can_be_filtered() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        candidate = Candidate(
            name="Test",
            email="test@example.com",
            preferred_roles="AI Engineer",
            preferred_locations="Remote",
        )
        db.add(candidate)
        db.commit()

        skill = Skill(name="python")
        db.add(skill)
        db.commit()
        db.add(CandidateSkill(candidate_id=candidate.id, skill_id=skill.id))
        db.add(Resume(candidate_id=candidate.id, filename="resume.txt", raw_text="Python AI engineering"))
        db.commit()

        save_job(db, {
            "title": "AI Engineer Intern",
            "company": "RemoteCo",
            "description": "Python AI",
            "location": "Remote",
            "remote": True,
            "skills": ["python"],
        })
        save_job(db, {
            "title": "Backend Developer",
            "company": "OfficeCo",
            "description": "Python backend",
            "location": "Bengaluru",
            "remote": False,
            "skills": ["python"],
        })
        db.commit()

        results = recommend_jobs(db, candidate.id, 10, remote=True)

        assert len(results) == 1
        assert results[0].job.title == "AI Engineer Intern"
