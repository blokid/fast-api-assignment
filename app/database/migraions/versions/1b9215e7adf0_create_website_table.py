"""create website table

Revision ID: 1b9215e7adf0
Revises: 6ba756b2a8cc
Create Date: 2025-02-18 09:42:10.362728

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func


# revision identifiers, used by Alembic.
revision = "1b9215e7adf0"
down_revision = "6ba756b2a8cc"
branch_labels = None
depends_on = None


def _create_websites_table() -> None:
    """Create the websites table with organization_id FK, timestamps, soft delete, and update trigger."""
    op.create_table(
        "websites",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "organization_id",
            sa.Integer,
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("url", sa.String(2083), unique=True, nullable=False),
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
        sa.Column(
            "deleted_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )

    # Reuse the existing updated_at trigger for websites
    op.execute(
        """
        CREATE TRIGGER update_website_modtime
            BEFORE UPDATE
            ON websites
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def upgrade() -> None:
    """Apply the migration."""
    _create_websites_table()


def downgrade() -> None:
    """Rollback the migration."""
    op.drop_table("websites")
    op.execute("DROP TRIGGER IF EXISTS update_website_modtime ON websites")
