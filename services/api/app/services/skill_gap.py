from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CandidateSkill, Skill
from app.services.recommendation_engine import recommend_jobs
from app.services.skill_normalization import normalize_skill


def analyze_skill_gaps(db: Session, candidate_id: int, job_limit: int = 10) -> tuple[int, list[dict[str, object]]]:
    recommendations = recommend_jobs(db, candidate_id, job_limit)
    candidate_skill_rows = db.scalars(
        select(Skill.name)
        .join(CandidateSkill, CandidateSkill.skill_id == Skill.id)
        .where(CandidateSkill.candidate_id == candidate_id)
    ).all()
    candidate_skills = {normalize_skill(skill) for skill in candidate_skill_rows}

    demand: Counter[str] = Counter()
    for recommendation in recommendations:
        for skill in recommendation.missing_skills:
            normalized = normalize_skill(skill)
            if normalized not in candidate_skills:
                demand[normalized] += 1

    gaps = [
        {
            "skill": skill,
            "priority": count,
            "jobs_requiring_skill": count,
            "reason": f"{count} of the analyzed recommended jobs require this skill and it is not currently in the candidate profile.",
        }
        for skill, count in demand.most_common()
    ]
    return len(recommendations), gaps
