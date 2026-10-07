from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.services.job_aggregator import ingest_source
from app.services.job_sources import DemoJobSource


def test_demo_source_can_be_ingested() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        count = ingest_source(db, DemoJobSource())
        db.commit()
        assert count > 0
