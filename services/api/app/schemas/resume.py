from pydantic import BaseModel


class ResumeRead(BaseModel):
    id: int
    candidate_id: int
    filename: str
    content_type: str | None
    extracted_skills: list[str]
    text_length: int
