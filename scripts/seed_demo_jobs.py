import json
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

API_DIR = Path(__file__).resolve().parents[1] / "services" / "api"
sys.path.insert(0, str(API_DIR))

from app.config import settings
from app.db import Base
from app.services.job_ingestion import save_job


def main() -> None:
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)

    data_path = API_DIR / "data" / "demo_jobs.json"
    jobs = json.loads(data_path.read_text(encoding="utf-8"))

    with Session(engine) as db:
        for payload in jobs:
            save_job(db, payload)
        db.commit()

    print(f"Seeded {len(jobs)} demo jobs.")


if __name__ == "__main__":
    main()
