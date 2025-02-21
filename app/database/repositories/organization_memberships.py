from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncConnection
from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.organization import OrganizationMembership
from app.schemas.organization_membership import OrganizationMembershipInDB


class OrganizationMembershipsRepository(BaseRepository):
    def __init__(self, conn: AsyncConnection) -> None:
        super().__init__(conn)

    @db_error_handler
    async def add_member(
        self, *, organization_id: int, user_id: int, role: str
    ) -> OrganizationMembership:
        membership = OrganizationMembership(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
        )
        self.connection.add(membership)
        await self.connection.commit()
        await self.connection.refresh(membership)
        return membership

    @db_error_handler
    async def remove_member(self, *, membership_id: int) -> None:
        query = OrganizationMembership.__table__.delete().where(
            OrganizationMembership.id == membership_id
        )
        await self.connection.execute(query)
        await self.connection.commit()

    @db_error_handler
    async def get_memberships_by_user(
        self, *, user_id: int
    ) -> list[OrganizationMembership]:
        """Get all memberships for a user."""
        query = select(OrganizationMembership).where(
            OrganizationMembership.user_id == user_id
        )
        raw_results = await self.connection.execute(query)
        return raw_results.scalars().all()

    @db_error_handler
    async def get_members_by_organization(
        self, *, organization_id: int
    ) -> list[OrganizationMembership]:
        """Get all members of an organization."""
        query = select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id
        )
        raw_results = await self.connection.execute(query)
        return raw_results.scalars().all()

    @db_error_handler
    async def update_member_role(
        self, *, organization_id: int, user_id: int, role: str
    ) -> OrganizationMembership:
        """Update a member's role in an organization."""
        query = select(OrganizationMembership).where(
            and_(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.user_id == user_id,
            )
        )
        raw_result = await self.connection.execute(query)
        membership = raw_result.scalar_one_or_none()

        if membership:
            membership.role = role
            self.connection.add(membership)
            await self.connection.commit()
            await self.connection.refresh(membership)
            return membership

        raise ValueError("Membership not found")

    @db_error_handler
    async def get_membership(
        self, *, user_id: int, organization_id: int
    ) -> OrganizationMembership:
        """Retrieve a membership record for a specific user and organization."""
        query = (
            select(OrganizationMembership)
            .where(
                and_(
                    OrganizationMembership.organization_id == organization_id,
                    OrganizationMembership.user_id == user_id,
                )
            )
            .limit(1)
        )
        raw_result = await self.connection.execute(query)
        # Using scalar_one_or_none() to return a single result or None if not found.
        membership = raw_result.scalar_one_or_none()
        return membership
