"""organization_invites table

Revision ID: 3c261e5a1c90
Revises: 11523ef9ea2a
Create Date: 2025-02-16 17:30:40.074325

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3c261e5a1c90"
down_revision = "11523ef9ea2a"
branch_labels = None
depends_on = None


def _timestamps() -> tuple[sa.Column, sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
            server_default=sa.func.now(),
            onupdate=sa.func.current_timestamp(),
        ),
        sa.Column(
            "deleted_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )


def _create_organization_invites_table() -> None:
    op.create_table(
        "organization_invites",
        sa.Column(
            "organization_id",
            sa.Integer(),
            sa.ForeignKey("organizations.id"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("email", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column(
            "is_accepted", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        *_timestamps(),
    )


def upgrade() -> None:
    _create_organization_invites_table()


def downgrade() -> None:
    op.drop_table("organization_invites")
