"""add job metadata and recommendation run ids
Revision ID: 0005
Revises: 0004
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("jobs", sa.Column("salary_min", sa.Float(), nullable=True))
    op.add_column("jobs", sa.Column("salary_max", sa.Float(), nullable=True))
    op.add_column("jobs", sa.Column("experience_min_years", sa.Float(), nullable=True))
    op.add_column("jobs", sa.Column("experience_max_years", sa.Float(), nullable=True))
    op.add_column("recommendations", sa.Column("run_id", sa.String(length=36), nullable=True))
    op.create_index("ix_recommendations_run_id", "recommendations", ["run_id"])

def downgrade() -> None:
    op.drop_index("ix_recommendations_run_id", table_name="recommendations")
    op.drop_column("recommendations", "run_id")
    op.drop_column("jobs", "experience_max_years")
    op.drop_column("jobs", "experience_min_years")
    op.drop_column("jobs", "salary_max")
    op.drop_column("jobs", "salary_min")
