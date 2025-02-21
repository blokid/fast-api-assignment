"""add_relationships_organization_memberships

Revision ID: ef680e367ea4
Revises: ab87ab6fe487
Create Date: 2025-02-16 13:46:09.300563

"""

from alembic import op
import sqlalchemy as sa


revision = "ef680e367ea4"
down_revision = "ab87ab6fe487"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration to add foreign key constraints."""

    op.create_foreign_key(
        "fk_organization_memberships_user",
        "organization_memberships",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_organization_memberships_organization",
        "organization_memberships",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Rollback the migration by removing foreign keys."""
    op.drop_constraint(
        "fk_organization_memberships_user",
        "organization_memberships",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_organization_memberships_organization",
        "organization_memberships",
        type_="foreignkey",
    )
