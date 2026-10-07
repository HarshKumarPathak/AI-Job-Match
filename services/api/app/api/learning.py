from fastapi import APIRouter, Query

from app.schemas.learning import LearningResourceRead
from app.services.learning import resources_for_skills

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("", response_model=list[LearningResourceRead])
def get_learning_resources(
    skills: list[str] = Query(default=[]),
) -> list[LearningResourceRead]:
    return [
        LearningResourceRead(
            skill=item.skill,
            level=item.level,
            resource_type=item.resource_type,
            title=item.title,
            url=item.url,
            reason=f"Recommended because {item.skill} is a useful skill to improve.",
        )
        for item in resources_for_skills(skills)
    ]
