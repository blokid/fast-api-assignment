"""add is_verified to user model

Revision ID: c60282a5a0db
Revises: b2437a6523e3
Create Date: 2025-02-15 03:33:42.627117

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c60282a5a0db"
down_revision = "b2437a6523e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_verified", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_verified")
