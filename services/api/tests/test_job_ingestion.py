from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db import Base
from app.models import JobSkill, Skill
from app.services.job_ingestion import save_job


def test_job_ingestion_normalizes_and_deduplicates() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        first = save_job(
            db,
            {
                "external_id": "job-1",
                "source": "demo",
                "title": "AI Engineer Intern",
                "company": "Example",
                "skills": ["Python", "py", "SQL"],
            },
        )
        db.commit()

        second = save_job(
            db,
            {
                "external_id": "job-1",
                "source": "demo",
                "title": "AI Engineer Intern",
                "company": "Example",
                "skills": ["Python", "SQL"],
            },
        )
        db.commit()

        assert first.id == second.id
        assert second.title == "AI Engineer Intern"

        skill_names = db.scalars(
            select(Skill.name)
            .join(JobSkill, JobSkill.skill_id == Skill.id)
            .where(JobSkill.job_id == second.id)
            .order_by(Skill.name)
        ).all()
        assert skill_names == ["python", "sql"]
