"""add users for application authentication

Revision ID: 0006
Revises: 0005
"""

from alembic import op
import sqlalchemy as sa


revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["candidate_id"],
            ["candidates.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("candidate_id"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_candidate_id", "users", ["candidate_id"])


def downgrade() -> None:
    op.drop_index("ix_users_candidate_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
