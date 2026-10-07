"""Initial candidate and job schema."""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160)),
        sa.Column("email", sa.String(length=320), unique=True),
        sa.Column("preferred_roles", sa.Text(), nullable=False, server_default=""),
        sa.Column("preferred_locations", sa.Text(), nullable=False, server_default=""),
        sa.Column("experience_years", sa.Float(), nullable=False, server_default="0"),
        sa.Column("education", sa.Text()),
    )
    op.create_index("ix_candidates_email", "candidates", ["email"], unique=True)

    op.create_table("resumes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120)),
        sa.Column("raw_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_resumes_candidate_id", "resumes", ["candidate_id"])

    op.create_table("skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
    )
    op.create_index("ix_skills_name", "skills", ["name"], unique=True)

    op.create_table("candidate_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("level", sa.String(length=40)),
        sa.UniqueConstraint("candidate_id", "skill_id", name="uq_candidate_skill"),
    )

    op.create_table("jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=255)),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("location", sa.String(length=255)),
        sa.Column("remote", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("employment_type", sa.String(length=80)),
        sa.Column("apply_url", sa.Text()),
        sa.Column("source", sa.String(length=120)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_jobs_external_id", "jobs", ["external_id"])
    op.create_index("ix_jobs_title", "jobs", ["title"])
    op.create_index("ix_jobs_company", "jobs", ["company"])
    op.create_index("ix_jobs_source", "jobs", ["source"])

    op.create_table("job_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),
    )

    op.create_table("recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("matched_skills", sa.Text(), nullable=False, server_default=""),
        sa.Column("missing_skills", sa.Text(), nullable=False, server_default=""),
        sa.Column("reasons", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_recommendations_candidate_id", "recommendations", ["candidate_id"])
    op.create_index("ix_recommendations_job_id", "recommendations", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_recommendations_job_id", table_name="recommendations")
    op.drop_index("ix_recommendations_candidate_id", table_name="recommendations")
    op.drop_table("recommendations")
    op.drop_table("job_skills")
    op.drop_index("ix_jobs_source", table_name="jobs")
    op.drop_index("ix_jobs_company", table_name="jobs")
    op.drop_index("ix_jobs_title", table_name="jobs")
    op.drop_index("ix_jobs_external_id", table_name="jobs")
    op.drop_table("jobs")
    op.drop_table("candidate_skills")
    op.drop_index("ix_skills_name", table_name="skills")
    op.drop_table("skills")
    op.drop_index("ix_resumes_candidate_id", table_name="resumes")
    op.drop_table("resumes")
    op.drop_index("ix_candidates_email", table_name="candidates")
    op.drop_table("candidates")