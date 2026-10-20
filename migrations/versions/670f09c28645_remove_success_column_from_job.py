"""Remove success column from job

Revision ID: 670f09c28645
Revises: 4b6a9d2e10f3
Create Date: 2026-10-20 16:42:49.047721

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '670f09c28645'
down_revision = '4b6a9d2e10f3'
branch_labels = None
depends_on = None


def upgrade():
       op.drop_column("job", "success")


def downgrade():
       op.add_column("job", sa.Column(
        "success", sa.Boolean(), nullable=True,
    ))