"""create organizations table

Revision ID: af9a0e8d22a6
Revises: f6a845604823
Create Date: 2025-02-16 13:36:52.955402

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import func


# revision identifiers, used by Alembic.
revision = "af9a0e8d22a6"
down_revision = "f6a845604823"
branch_labels = None
depends_on = None


def _create_organizations_table() -> None:
    """Create the organizations table with timestamps and update trigger."""
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
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

    # Reuse the existing updated_at trigger for organizations
    op.execute(
        """
        CREATE TRIGGER update_organization_modtime
            BEFORE UPDATE
            ON organizations
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def upgrade() -> None:
    """Apply the migration."""
    _create_organizations_table()


def downgrade() -> None:
    """Rollback the migration."""
    op.drop_table("organizations")
    op.execute("DROP TRIGGER IF EXISTS update_organization_modtime ON organizations")
