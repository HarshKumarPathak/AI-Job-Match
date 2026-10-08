from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Job
from app.services.job_ingestion import save_job


def test_job_metadata_is_persisted():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        job = save_job(
            db,
            {
                "title": "ML Engineer",
                "company": "Example",
                "salary_min": 50000,
                "salary_max": 90000,
                "experience_min_years": 1,
                "experience_max_years": 3,
            },
        )
        assert job.salary_min == 50000
        assert job.experience_max_years == 3


def test_job_metadata_is_updated_on_reingestion():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        first = save_job(
            db,
            {
                "external_id": "job-1",
                "source": "test",
                "title": "ML Engineer",
                "company": "Example",
                "salary_min": 50000,
                "salary_max": 90000,
                "experience_min_years": 1,
                "experience_max_years": 3,
            },
        )
        db.commit()

        updated = save_job(
            db,
            {
                "external_id": "job-1",
                "source": "test",
                "title": "ML Engineer",
                "company": "Example",
                "salary_min": 60000,
                "salary_max": 100000,
                "experience_min_years": 2,
                "experience_max_years": 4,
            },
        )

        assert updated.id == first.id
        assert updated.salary_min == 60000
        assert updated.salary_max == 100000
        assert updated.experience_min_years == 2
        assert updated.experience_max_years == 4
