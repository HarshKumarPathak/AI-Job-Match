from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.jobs import list_jobs
from app.db import Base
from app.models import Job


def test_job_filters_search_remote_and_location() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        db.add_all([
            Job(title="AI Engineer Intern", company="A", description="python", location="Remote", remote=True),
            Job(title="Backend Developer", company="B", description="python", location="Bengaluru", remote=False),
        ])
        db.commit()

        results = list_jobs(q="AI", remote=True, location="Remote", db=db)

        assert len(results) == 1
        assert results[0].title == "AI Engineer Intern"
