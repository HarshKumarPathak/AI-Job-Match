from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Candidate, CandidateSkill, Resume, Skill
from app.schemas.resume import ResumeRead
from app.services.resume_parser import extract_text
from app.services.skill_extractor import extract_skills
from app.services.resume_profile import infer_profile

router = APIRouter(prefix="/candidates/{candidate_id}/resumes", tags=["resumes"])


@router.post("", response_model=ResumeRead, status_code=201)
async def upload_resume(
    candidate_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ResumeRead:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    data = await file.read()
    try:
        text = extract_text(file.filename or "resume.txt", data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from resume")

    skills = extract_skills(text)
    inferred = infer_profile(text)
    resume = Resume(
        candidate_id=candidate_id,
        filename=file.filename or "resume",
        content_type=file.content_type,
        raw_text=text,
    )
    db.add(resume)

    for skill_name in skills:
        skill = db.scalar(select(Skill).where(Skill.name == skill_name))
        if skill is None:
            skill = Skill(name=skill_name)
            db.add(skill)
            db.flush()

        existing = db.scalar(
            select(CandidateSkill).where(
                CandidateSkill.candidate_id == candidate_id,
                CandidateSkill.skill_id == skill.id,
            )
        )
        if existing is None:
            db.add(CandidateSkill(candidate_id=candidate_id, skill_id=skill.id))

    if inferred["education"] and not candidate.education:
        candidate.education = str(inferred["education"])
    if inferred["experience_years"] and candidate.experience_years == 0:
        candidate.experience_years = float(inferred["experience_years"])
    if inferred["preferred_roles"] and not candidate.preferred_roles:
        candidate.preferred_roles = "\n".join(inferred["preferred_roles"])

    db.commit()
    db.refresh(resume)

    return ResumeRead(
        id=resume.id,
        candidate_id=resume.candidate_id,
        filename=resume.filename,
        content_type=resume.content_type,
        extracted_skills=skills,
        text_length=len(text),
    )
