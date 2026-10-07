from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CandidateSkill, Skill
from app.services.skill_normalization import normalize_skills


def save_candidate_skills(db: Session, candidate_id: int, skills: list[str]) -> list[str]:
    normalized = normalize_skills(skills)
    for skill_name in normalized:
        skill = db.scalar(select(Skill).where(Skill.name == skill_name))
        if skill is None:
            skill = Skill(name=skill_name)
            db.add(skill)
            db.flush()
        exists = db.scalar(
            select(CandidateSkill).where(
                CandidateSkill.candidate_id == candidate_id,
                CandidateSkill.skill_id == skill.id,
            )
        )
        if exists is None:
            db.add(CandidateSkill(candidate_id=candidate_id, skill_id=skill.id))
    return normalized
