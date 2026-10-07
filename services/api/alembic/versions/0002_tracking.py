"""add saved jobs and application tracking

Revision ID: 0002
Revises: 0001
"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "saved_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("candidate_id", "job_id", name="uq_saved_job"),
    )
    op.create_index("ix_saved_jobs_candidate_id", "saved_jobs", ["candidate_id"])
    op.create_index("ix_saved_jobs_job_id", "saved_jobs", ["job_id"])

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="saved"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("applied_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("candidate_id", "job_id", name="uq_application"),
    )
    op.create_index("ix_applications_candidate_id", "applications", ["candidate_id"])
    op.create_index("ix_applications_job_id", "applications", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_applications_job_id", table_name="applications")
    op.drop_index("ix_applications_candidate_id", table_name="applications")
    op.drop_table("applications")
    op.drop_index("ix_saved_jobs_job_id", table_name="saved_jobs")
    op.drop_index("ix_saved_jobs_candidate_id", table_name="saved_jobs")
    op.drop_table("saved_jobs")
