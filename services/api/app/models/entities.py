from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"), unique=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Candidate(Base):
    __tablename__ = "candidates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(160))
    email: Mapped[str | None] = mapped_column(String(320), unique=True, index=True)
    preferred_roles: Mapped[str] = mapped_column(Text, default="")
    preferred_locations: Mapped[str] = mapped_column(Text, default="")
    experience_years: Mapped[float] = mapped_column(Float, default=0.0)
    education: Mapped[str | None] = mapped_column(Text)
    resumes: Mapped[list["Resume"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")
    skills: Mapped[list["CandidateSkill"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str | None] = mapped_column(String(120))
    raw_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    candidate: Mapped[Candidate] = relationship(back_populates="resumes")


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"
    __table_args__ = (UniqueConstraint("candidate_id", "skill_id", name="uq_candidate_skill"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))
    level: Mapped[str | None] = mapped_column(String(40))
    candidate: Mapped[Candidate] = relationship(back_populates="skills")
    skill: Mapped[Skill] = relationship()


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    company: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    location: Mapped[str | None] = mapped_column(String(255))
    remote: Mapped[bool] = mapped_column(Boolean, default=False)
    employment_type: Mapped[str | None] = mapped_column(String(80))
    apply_url: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(120), index=True)
    salary_min: Mapped[float | None] = mapped_column(Float)
    salary_max: Mapped[float | None] = mapped_column(Float)
    experience_min_years: Mapped[float | None] = mapped_column(Float)
    experience_max_years: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobSkill(Base):
    __tablename__ = "job_skills"
    __table_args__ = (UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))
    skill: Mapped[Skill] = relationship()


class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    score: Mapped[float] = mapped_column(Float)
    matched_skills: Mapped[str] = mapped_column(Text, default="")
    missing_skills: Mapped[str] = mapped_column(Text, default="")
    reasons: Mapped[str] = mapped_column(Text, default="")
    run_id: Mapped[str | None] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SavedJob(Base):
    __tablename__ = "saved_jobs"
    __table_args__ = (UniqueConstraint("candidate_id", "job_id", name="uq_saved_job"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("candidate_id", "job_id", name="uq_application"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(40), default="saved")
    notes: Mapped[str] = mapped_column(Text, default="")
    applied_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobAlert(Base):
    __tablename__ = "job_alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), index=True)
    minimum_score: Mapped[float] = mapped_column(Float, default=70.0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
