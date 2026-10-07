from pydantic import BaseModel


class LearningResourceRead(BaseModel):
    skill: str
    level: str
    resource_type: str
    title: str
    url: str
    reason: str
