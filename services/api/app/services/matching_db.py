from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.candidate import CandidateProfile
from app.domain.job import Job as DomainJob
from app.models import Candidate, CandidateSkill, Job, JobSkill, Resume, Skill
from app.services.matching import MatchResult, explain_match


def _split_lines(value: str) -> set[str]:
    return {item.strip() for item in value.splitlines() if item.strip()}


def get_candidate_profile(db: Session, candidate_id: int) -> CandidateProfile:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise ValueError("Candidate not found")

    skills = db.scalars(
        select(Skill.name)
        .join(CandidateSkill, CandidateSkill.skill_id == Skill.id)
        .where(CandidateSkill.candidate_id == candidate_id)
    ).all()

    resume = db.scalar(
        select(Resume)
        .where(Resume.candidate_id == candidate_id)
        .order_by(Resume.created_at.desc())
    )

    return CandidateProfile(
        skills=set(skills),
        preferred_roles=_split_lines(candidate.preferred_roles),
        preferred_locations=_split_lines(candidate.preferred_locations),
        experience_years=candidate.experience_years,
        education=candidate.education,
        resume_text=resume.raw_text if resume else "",
    )


def match_candidate_to_job(db: Session, candidate_id: int, job_id: int) -> MatchResult:
    candidate = get_candidate_profile(db, candidate_id)
    job = db.get(Job, job_id)
    if job is None:
        raise ValueError("Job not found")

    skills = db.scalars(
        select(Skill.name)
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .where(JobSkill.job_id == job_id)
    ).all()

    domain_job = DomainJob(
        id=str(job.id),
        title=job.title,
        company=job.company,
        description=job.description,
        skills=set(skills),
        location=job.location,
        remote=job.remote,
        employment_type=job.employment_type,
        apply_url=job.apply_url,
        source=job.source,
    )
    return explain_match(candidate, domain_job)
