import json
from pathlib import Path
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

API_DIR = Path(__file__).resolve().parents[1] / "services" / "api"
sys.path.insert(0, str(API_DIR))

from app.config import settings
from app.db import Base
from app.models import Candidate, CandidateSkill, Skill
from app.services.job_ingestion import save_job
from app.services.skill_normalization import normalize_skill


def main() -> None:
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)

    data_path = API_DIR / "data" / "demo_jobs.json"
    jobs = json.loads(data_path.read_text(encoding="utf-8"))

    with Session(engine) as db:
        candidate = db.scalar(select(Candidate).where(Candidate.email == "demo@aijobmatch.local"))
        if candidate is None:
            candidate = Candidate(
                name="Demo Candidate",
                email="demo@aijobmatch.local",
                preferred_roles="AI Engineer\nBackend Developer\nData Scientist",
                preferred_locations="Remote\nBengaluru",
                experience_years=0.0,
                education="B.Tech CSE (AI & ML)",
            )
            db.add(candidate)
            db.flush()

        for skill_name in ["Python", "SQL", "Machine Learning", "Pandas", "Git"]:
            normalized = normalize_skill(skill_name)
            skill = db.scalar(select(Skill).where(Skill.name == normalized))
            if skill is None:
                skill = Skill(name=normalized)
                db.add(skill)
                db.flush()
            exists = db.scalar(
                select(CandidateSkill).where(
                    CandidateSkill.candidate_id == candidate.id,
                    CandidateSkill.skill_id == skill.id,
                )
            )
            if exists is None:
                db.add(CandidateSkill(candidate_id=candidate.id, skill_id=skill.id))

        for payload in jobs:
            save_job(db, payload)

        db.commit()
        print(f"Demo candidate id: {candidate.id}")
        print(f"Seeded {len(jobs)} demo jobs.")


if __name__ == "__main__":
    main()
