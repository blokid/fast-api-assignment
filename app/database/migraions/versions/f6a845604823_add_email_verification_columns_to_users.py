"""add email verification columns to users

Revision ID: f6a845604823
Revises: b2437a6523e3
Create Date: 2025-02-15 19:15:08.748779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6a845604823'
down_revision = 'b2437a6523e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration - Add email verification fields to users table."""
    op.add_column('users', sa.Column(
        'email_verified',
        sa.Boolean(),
        nullable=False,
        server_default=sa.text('false'),
        comment="Indicates if user's email is verified"
    ))

    # Add 'email_verification_token' column (string)
    op.add_column('users', sa.Column(
        'email_verification_token',
        sa.String(length=255),
        nullable=True,
        comment="Token for email verification"
    ))

    # Add 'email_verified_at' column (timestamp)
    op.add_column('users', sa.Column(
        'email_verified_at',
        sa.TIMESTAMP(timezone=True),
        nullable=True,
        comment="Timestamp when the user verified their email"
    ))
    pass


def downgrade() -> None:
    """Revert the migration - Remove email verification fields from users table."""
    # Remove 'email_verified' column
    op.drop_column('users', 'email_verified')

    # Remove 'email_verification_token' column
    op.drop_column('users', 'email_verification_token')

    # Remove 'email_verified_at' column
    op.drop_column('users', 'email_verified_at')
    pass
