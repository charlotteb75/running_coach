"""Add a unique Garmin activity identifier, preserving legacy runs.

Revision ID: a71d8c902e4f
Revises: 670f09c28645
"""

from alembic import op
import sqlalchemy as sa


revision = "a71d8c902e4f"
down_revision = "670f09c28645"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "running_history",
        sa.Column("id_garmin_activity", sa.BigInteger(), nullable=False),
    )
    op.create_unique_constraint(
        "uq_running_history_id_garmin_activity",
        "running_history",
        ["id_garmin_activity"],
    )


def downgrade():
    op.drop_constraint(
        "uq_running_history_id_garmin_activity", "running_history", type_="unique"
    )
    op.drop_column("running_history", "id_garmin_activity")
