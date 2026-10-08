from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Candidate, CandidateSkill, Job, Recommendation, Resume, Skill, User
from app.services.job_ingestion import save_job
from app.api.recommendations import recommendation_history
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



def test_recommendation_history_groups_rows_by_run() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        candidate = Candidate(name="History User", email="history@example.com")
        db.add(candidate)
        db.commit()

        user = User(
            email="history@example.com",
            password_hash="test-hash",
            candidate_id=candidate.id,
        )
        db.add(user)
        db.add_all([
            Job(id=1, title="Python Intern", company="Example"),
            Job(id=2, title="AI Intern", company="Example"),
        ])
        db.commit()

        db.add_all([
            Recommendation(
                candidate_id=candidate.id,
                job_id=1,
                score=82,
                matched_skills="python",
                missing_skills="docker",
                reasons="skill match",
                run_id="run-a",
                    created_at=datetime(2026, 1, 1, 12, 0, 0),
            ),
            Recommendation(
                candidate_id=candidate.id,
                job_id=2,
                score=76,
                matched_skills="ai",
                missing_skills="sql",
                reasons="role match",
                run_id="run-a",
            ),
            Recommendation(
                candidate_id=candidate.id,
                job_id=1,
                score=88,
                matched_skills="python",
                missing_skills="",
                reasons="strong match",
                run_id="run-b",
                    created_at=datetime(2026, 1, 1, 12, 1, 0),
            ),
        ])
        db.commit()

        runs = recommendation_history(candidate.id, limit=10, db=db, user=user)

        assert len(runs) == 2
        assert runs[0]["run_id"] == "run-b"
        assert len(runs[1]["recommendations"]) == 2
        assert runs[1]["run_id"] == "run-a"
