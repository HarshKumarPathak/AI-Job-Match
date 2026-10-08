from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Candidate, CandidateSkill, Recommendation, Resume, Skill
from app.services.job_ingestion import save_job
from app.services.recommendation_engine import recommend_jobs
from app.services.recommendation_persistence import persist_recommendations


def test_recommendations_are_persisted_as_separate_runs() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        candidate = Candidate(
            name="Persist User",
            email="persist@example.com",
            preferred_roles="AI Engineer",
            preferred_locations="Remote",
        )
        db.add(candidate)
        db.commit()

        skill = Skill(name="python")
        db.add(skill)
        db.commit()
        db.add(CandidateSkill(candidate_id=candidate.id, skill_id=skill.id))
        db.add(
            Resume(
                candidate_id=candidate.id,
                filename="resume.txt",
                raw_text="Python AI engineering",
            )
        )
        db.commit()

        save_job(
            db,
            {
                "title": "AI Engineer",
                "company": "Example",
                "description": "Python AI",
                "location": "Remote",
                "remote": True,
                "skills": ["python"],
            },
        )
        db.commit()

        ranked = recommend_jobs(db, candidate.id, 10)
        assert persist_recommendations(db, candidate.id, ranked) == 1
        assert persist_recommendations(db, candidate.id, ranked) == 1

        history = db.scalars(
            select(Recommendation)
            .where(Recommendation.candidate_id == candidate.id)
            .order_by(Recommendation.created_at.asc(), Recommendation.id.asc())
        ).all()

        assert len(history) == 2
        assert history[0].job_id == ranked[0].job.id
        assert history[0].score == ranked[0].score
        assert history[0].run_id
        assert history[1].run_id
        assert history[0].run_id != history[1].run_id
