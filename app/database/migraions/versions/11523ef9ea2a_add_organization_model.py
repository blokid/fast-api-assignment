"""add organization model

Revision ID: 11523ef9ea2a
Revises: c60282a5a0db
Create Date: 2025-02-16 05:54:05.007548

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "11523ef9ea2a"
down_revision = "c60282a5a0db"
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


def _create_organization_table() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        *_timestamps(),
    )
    op.create_table(
        "organization_users",
        sa.Column(
            "organization_id",
            sa.Integer(),
            sa.ForeignKey("organizations.id"),
            primary_key=True,
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("role", sa.String(length=16), nullable=False),
        *_timestamps(),
    )


def upgrade() -> None:
    _create_organization_table()


def downgrade() -> None:
    op.drop_table("organization_users")
    op.drop_table("organizations")
