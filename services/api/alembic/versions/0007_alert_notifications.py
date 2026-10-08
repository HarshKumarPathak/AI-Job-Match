"""track delivered job alert notifications

Revision ID: 0007
Revises: 0006
"""
from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alert_notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_id", sa.Integer(), sa.ForeignKey("job_alerts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("alert_id", "job_id", name="uq_alert_notification"),
    )
    op.create_index("ix_alert_notifications_alert_id", "alert_notifications", ["alert_id"])
    op.create_index("ix_alert_notifications_job_id", "alert_notifications", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_alert_notifications_job_id", table_name="alert_notifications")
    op.drop_index("ix_alert_notifications_alert_id", table_name="alert_notifications")
    op.drop_table("alert_notifications")
