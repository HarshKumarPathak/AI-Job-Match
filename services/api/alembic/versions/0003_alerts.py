"""add job alerts

Revision ID: 0003
Revises: 0002
"""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("minimum_score", sa.Float(), nullable=False, server_default="70"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_job_alerts_candidate_id", "job_alerts", ["candidate_id"])


def downgrade() -> None:
    op.drop_index("ix_job_alerts_candidate_id", table_name="job_alerts")
    op.drop_table("job_alerts")
