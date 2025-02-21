"""create website memberships table

Revision ID: 912c557ebec0
Revises: 1b9215e7adf0
Create Date: 2025-02-18 10:00:40.362524

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

# revision identifiers, used by Alembic.
revision = "912c557ebec0"
down_revision = "1b9215e7adf0"
branch_labels = None
depends_on = None


def _create_website_memberships_table() -> None:
    """Create the website_memberships table with constraints and triggers."""
    op.create_table(
        "website_memberships",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "website_id",
            sa.Integer,
            sa.ForeignKey("websites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum("admin", "member", name="website_role_enum"),
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
        CREATE TRIGGER update_website_membership_modtime
            BEFORE UPDATE
            ON website_memberships
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def upgrade() -> None:
    """Apply the migration."""
    _create_website_memberships_table()

    # Add composite unique constraint for user_id and website_id
    op.create_unique_constraint(
        "uq_user_website",
        "website_memberships",
        ["user_id", "website_id"],
    )


def downgrade() -> None:
    """Rollback the migration."""
    op.drop_constraint(
        "uq_user_website",
        "website_memberships",
        type_="unique",
    )
    op.drop_table("website_memberships")
    op.execute(
        "DROP TRIGGER IF EXISTS update_website_membership_modtime ON website_memberships"
    )
    op.execute("DROP TYPE IF EXISTS website_role_enum")
