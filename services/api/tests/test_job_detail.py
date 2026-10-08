from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.jobs import get_job
from app.db import Base
from app.models import Job

def test_job_detail_returns_job():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        job = Job(title="AI Intern", company="Example", description="Python", salary_min=30000, salary_max=50000)
        db.add(job)
        db.commit()
        loaded = get_job(job.id, db)
        assert loaded.title == "AI Intern"
        assert loaded.salary_max == 50000
