"""Replace stored day completion with an explicit rest-day flag.

Revision ID: 4b6a9d2e10f3
Revises: 8e2b7c4d91a0

Existing test rows receive True, matching the current model default.
The old completion values are discarded, not renamed or converted.
"""

from alembic import op
import sqlalchemy as sa


revision = "4b6a9d2e10f3"
down_revision = "8e2b7c4d91a0"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("training_day", sa.Column(
        "is_rest_day", sa.Boolean(), nullable=False, server_default=sa.true(),
    ))
    op.drop_column("training_day", "training_day_completed")
    op.alter_column("training_day", "is_rest_day", server_default=None)


def downgrade():
    # Restore the old column, but not its discarded values.
    op.add_column("training_day", sa.Column(
        "training_day_completed", sa.Boolean(), nullable=True,
    ))
    op.drop_column("training_day", "is_rest_day")
