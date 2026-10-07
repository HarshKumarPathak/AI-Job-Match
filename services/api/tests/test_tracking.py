from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Candidate, Job
from app.schemas.tracking import ApplicationCreate, SavedJobCreate
from app.api.tracking import create_application, save_job_for_candidate


def test_save_and_apply() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        candidate = Candidate(name="Test")
        job = Job(title="Python Intern", company="Example")
        db.add_all([candidate, job])
        db.commit()

        saved = save_job_for_candidate(
            SavedJobCreate(candidate_id=candidate.id, job_id=job.id), db
        )
        application = create_application(
            ApplicationCreate(candidate_id=candidate.id, job_id=job.id, status="applied"),
            db,
        )

        assert saved.job_id == job.id
        assert application.status == "applied"
        assert application.applied_at is not None
