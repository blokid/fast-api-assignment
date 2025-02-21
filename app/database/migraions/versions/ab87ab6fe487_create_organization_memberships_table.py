"""create organization_memberships table

Revision ID: ab87ab6fe487
Revises: af9a0e8d22a6
Create Date: 2025-02-16 13:41:25.756425

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import func


# revision identifiers, used by Alembic.
revision = "ab87ab6fe487"
down_revision = "af9a0e8d22a6"
branch_labels = None
depends_on = None


def _create_organization_memberships_table() -> None:
    """Create the organization_memberships table with proper constraints."""
    op.create_table(
        "organization_memberships",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.Integer,
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum("admin", "member", name="organization_role_enum"),
            nullable=False,
            server_default="member",
        ),
        sa.Column(
            "joined_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
            server_default=func.now(),
            onupdate=func.current_timestamp(),
        ),
    )

    op.execute(
        """
        CREATE TRIGGER update_organization_membership_modtime
            BEFORE UPDATE
            ON organization_memberships
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def upgrade() -> None:
    """Apply the migration."""
    _create_organization_memberships_table()


def downgrade() -> None:
    """Rollback the migration."""
    op.drop_table("organization_memberships")
    op.execute(
        "DROP TRIGGER IF EXISTS update_organization_membership_modtime ON organization_memberships"
    )
    op.execute("DROP TYPE IF EXISTS organization_role_enum")
