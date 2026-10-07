from sqlalchemy.orm import Session

from app.services.job_ingestion import save_job
from app.services.job_sources import JobSource


def ingest_source(db: Session, source: JobSource) -> int:
    jobs = source.fetch_jobs()
    for payload in jobs:
        save_job(db, payload)
    return len(jobs)
