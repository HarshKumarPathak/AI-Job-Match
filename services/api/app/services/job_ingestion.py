from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Job, JobSkill, Skill
from app.services.skill_normalization import normalize_skills


def save_job(db: Session, payload: dict) -> Job:
    external_id = payload.get("external_id")
    source = payload.get("source")

    job = None
    if external_id and source:
        job = db.scalar(
            select(Job).where(Job.external_id == external_id, Job.source == source)
        )

    if job is None:
        job = Job(
            external_id=external_id,
            title=payload["title"].strip(),
            company=payload["company"].strip(),
            description=payload.get("description", "").strip(),
            location=payload.get("location"),
            remote=bool(payload.get("remote", False)),
            employment_type=payload.get("employment_type"),
            apply_url=payload.get("apply_url"),
            source=source,
            salary_min=payload.get("salary_min"),
            salary_max=payload.get("salary_max"),
            experience_min_years=payload.get("experience_min_years"),
            experience_max_years=payload.get("experience_max_years"),
        )
        db.add(job)
        db.flush()
    else:
        job.title = payload["title"].strip()
        job.company = payload["company"].strip()
        job.description = payload.get("description", "").strip()
        job.location = payload.get("location")
        job.remote = bool(payload.get("remote", False))
        job.employment_type = payload.get("employment_type")
        job.apply_url = payload.get("apply_url")
        job.salary_min = payload.get("salary_min")
        job.salary_max = payload.get("salary_max")
        job.experience_min_years = payload.get("experience_min_years")
        job.experience_max_years = payload.get("experience_max_years")

    normalized_skills = normalize_skills(payload.get("skills", []))
    skill_ids: set[int] = set()

    for skill_name in normalized_skills:
        skill = db.scalar(select(Skill).where(Skill.name == skill_name))
        if skill is None:
            skill = Skill(name=skill_name)
            db.add(skill)
            db.flush()
        skill_ids.add(skill.id)

        exists = db.scalar(
            select(JobSkill).where(JobSkill.job_id == job.id, JobSkill.skill_id == skill.id)
        )
        if exists is None:
            db.add(JobSkill(job_id=job.id, skill_id=skill.id))

    existing_relations = db.scalars(
        select(JobSkill).where(JobSkill.job_id == job.id)
    ).all()
    for relation in existing_relations:
        if relation.skill_id not in skill_ids:
            db.delete(relation)

    return job
