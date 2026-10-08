"""Run a configured job source ingestion from the command line.

This intentionally stays small: deployment schedulers can invoke this script on a
schedule without introducing a second application framework.
"""

import argparse
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from app.services.job_aggregator import ingest_source
from app.services.job_sources import DemoJobSource
from app.services.arbeitnow_source import ArbeitnowJobSource


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

    print(f"Ingested {count} jobs from {source.name}")


if __name__ == "__main__":
    main()
