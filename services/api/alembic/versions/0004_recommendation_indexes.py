"""add recommendation indexes

Revision ID: 0004
Revises: 0003
"""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_recommendations_candidate_created_at",
        "recommendations",
        ["candidate_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_recommendations_candidate_created_at",
        table_name="recommendations",
    )
