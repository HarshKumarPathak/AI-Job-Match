from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.tracking import create_application, save_job_for_candidate
from app.db import Base
from app.models import Candidate, Job, User
from app.schemas.tracking import ApplicationCreate, SavedJobCreate


def test_save_and_apply() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        candidate = Candidate(name="Test", email="test@example.com")
        job = Job(title="Python Intern", company="Example")
        db.add_all([candidate, job])
        db.commit()

        user = User(
            email="test@example.com",
            password_hash="test-hash",
            candidate_id=candidate.id,
        )
        db.add(user)
        db.commit()

        saved = save_job_for_candidate(
            SavedJobCreate(candidate_id=candidate.id, job_id=job.id),
            db,
            user,
        )
        application = create_application(
            ApplicationCreate(candidate_id=candidate.id, job_id=job.id, status="applied"),
            db,
            user,
        )

        assert saved.job_id == job.id
        assert application.status == "applied"
        assert application.applied_at is not None
