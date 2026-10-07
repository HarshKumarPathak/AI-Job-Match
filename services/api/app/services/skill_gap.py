from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Job, JobSkill, Skill
from app.services.recommendation_engine import recommend_jobs
from ml.skills.normalization import normalize_skill


def analyze_skill_gaps(
    db: Session,
    candidate_id: int,
    job_limit: int = 10,
) -> tuple[int, list[dict[str, object]]]:
    recommendations = recommend_jobs(db, candidate_id, job_limit)

    candidate_skill_rows = db.scalars(
        select(Skill.name)
        .join(__import__("app.models", fromlist=["CandidateSkill"]).CandidateSkill)
        .where(
            __import__("app.models", fromlist=["CandidateSkill"]).CandidateSkill.candidate_id
            == candidate_id
        )
    ).all()
    candidate_skills = {normalize_skill(skill) for skill in candidate_skill_rows}

    demand: Counter[str] = Counter()

    for recommendation in recommendations:
        for skill in recommendation.missing_skills:
            normalized = normalize_skill(skill)
            if normalized not in candidate_skills:
                demand[normalized] += 1

    gaps = []
    for skill, count in demand.most_common():
        gaps.append(
            {
                "skill": skill,
                "priority": count,
                "jobs_requiring_skill": count,
                "reason": (
                    f"{count} of the analyzed recommended jobs require this skill "
                    "and it is not currently in the candidate profile."
                ),
            }
        )

    return len(recommendations), gaps
