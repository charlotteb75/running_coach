"""Move content columns from training_day to training (schema only).

Revision ID: 8e2b7c4d91a0
Revises: c236a83a3171
"""

from alembic import op
import sqlalchemy as sa


revision = "8e2b7c4d91a0"
down_revision = "c236a83a3171"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("training", sa.Column("content", sa.Text(), nullable=True))
    with op.batch_alter_table("training_day") as batch:
        batch.drop_column("content_running")
        batch.drop_column("content_strength")
        batch.drop_column("nb_trainings")
        batch.drop_column("training_day_duration")


def downgrade():
    # Restore the columns, not their former values.
    with op.batch_alter_table("training_day") as batch:
        batch.add_column(sa.Column("content_running", sa.String(), nullable=True))
        batch.add_column(sa.Column("content_strength", sa.String(), nullable=True))
        batch.add_column(sa.Column("nb_trainings", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("training_day_duration", sa.Integer(), nullable=True))
    op.drop_column("training", "content")
