"""trigger onupdate

Revision ID: 59c28dbeb4ca
Revises: e8e56d4c2f53
Create Date: 2025-02-17 07:40:40.330473

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "59c28dbeb4ca"
down_revision = "e8e56d4c2f53"
branch_labels = None
depends_on = None


def _create_updated_at_trigger() -> None:
    op.execute(
        """
        CREATE TRIGGER update_websites_modtime
            BEFORE UPDATE
            ON websites
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_website_users_modtime
            BEFORE UPDATE
            ON website_users
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_website_invites_modtime
            BEFORE UPDATE
            ON website_invites
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_organizations_modtime
            BEFORE UPDATE
            ON organizations
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_organization_users_modtime
            BEFORE UPDATE
            ON organization_users
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_organization_invites_modtime
            BEFORE UPDATE
            ON organization_invites
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def upgrade() -> None:
    _create_updated_at_trigger()


def downgrade() -> None:
    op.execute("DROP TRIGGER update_websites_modtime")
    op.execute("DROP TRIGGER update_website_users_modtime")
    op.execute("DROP TRIGGER update_website_invites_modtime")
    op.execute("DROP TRIGGER update_organizations_modtime")
    op.execute("DROP TRIGGER update_organization_users_modtime")
    op.execute("DROP TRIGGER update_organization_invites_modtime")
