"""add website model

Revision ID: e8e56d4c2f53
Revises: 3c261e5a1c90
Create Date: 2025-02-17 02:11:37.495738

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e8e56d4c2f53"
down_revision = "3c261e5a1c90"
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


def _create_website_table() -> None:
    op.create_table(
        "websites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "website_users",
        sa.Column(
            "website_id", sa.Integer(), sa.ForeignKey("websites.id"), primary_key=True
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("role", sa.String(length=16), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "website_invites",
        sa.Column(
            "website_id", sa.Integer(), sa.ForeignKey("websites.id"), primary_key=True
        ),
        sa.Column("email", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column(
            "is_accepted", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        *_timestamps(),
    )


def upgrade() -> None:
    _create_website_table()


def downgrade() -> None:
    op.drop_table("websites")
    op.drop_table("website_users")
    op.drop_table("website_invites")
