"""add unique id constraint to organization memberships table

Revision ID: 6ba756b2a8cc
Revises: b5d76a0cc028
Create Date: 2025-02-17 21:59:51.461055

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6ba756b2a8cc"
down_revision = "b5d76a0cc028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration to add composite unique constraint."""
    op.create_unique_constraint(
        "uq_user_organization",
        "organization_memberships",
        ["user_id", "organization_id"],
    )


def downgrade() -> None:
    """Rollback the migration by removing the composite unique constraint."""
    op.drop_constraint(
        "uq_user_organization",
        "organization_memberships",
        type_="unique",
    )
