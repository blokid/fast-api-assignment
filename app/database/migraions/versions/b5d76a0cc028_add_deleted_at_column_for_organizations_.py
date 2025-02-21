"""add deleted_at column for organizations table

Revision ID: b5d76a0cc028
Revises: ef680e367ea4
Create Date: 2025-02-16 15:16:34.307008

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b5d76a0cc028"
down_revision = "ef680e367ea4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add deleted_at column to organizations table."""
    op.add_column(
        "organizations",
        sa.Column(
            "deleted_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove deleted_at column from organizations table."""
    op.drop_column("organizations", "deleted_at")
