"""Run a configured job source ingestion from the command line.

This intentionally stays small: deployment schedulers can invoke this script on a
schedule without introducing a second application framework.
"""

import argparse
import os
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from app.models import AlertNotification, Candidate, JobAlert
from app.services.alert_service import (
    mark_new_notifications,
    matching_alert_jobs,
    send_alert_email,
)
from app.services.arbeitnow_source import ArbeitnowJobSource
from app.services.job_aggregator import ingest_source
from app.services.job_sources import DemoJobSource


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest jobs into AI Job Match")
    parser.add_argument("--source", choices=["demo", "arbeitnow"], default="demo")
    args = parser.parse_args()

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/ai_job_match",
    )
    engine = create_engine(database_url)

    source = DemoJobSource() if args.source == "demo" else ArbeitnowJobSource()
    with Session(engine) as db:
        count = ingest_source(db, source)
        db.commit()
        alert_candidates = 0
        emails_sent = 0
        for candidate_id in db.scalars(
            select(JobAlert.candidate_id).where(JobAlert.enabled.is_(True))
        ).all():
            alert, matches = matching_alert_jobs(db, candidate_id)
            if alert is None:
                continue
            new_matches = mark_new_notifications(db, alert, matches)
            alert_candidates += len(new_matches)
            if not new_matches:
                continue

            candidate = db.get(Candidate, candidate_id)
            if candidate and send_alert_email(candidate, new_matches):
                emails_sent += 1

            # Record detection even when SMTP is disabled so the same job is not
            # treated as "new" on every scheduler cycle.
            for item in new_matches:
                db.add(
                    AlertNotification(
                        alert_id=alert.id,
                        job_id=item.job.id,
                        score=item.score,
                    )
                )
            db.commit()

    print(
        f"Ingested {count} jobs from {source.name}; "
        f"{alert_candidates} new alert matches; {emails_sent} emails sent"
    )


if __name__ == "__main__":
    main()
