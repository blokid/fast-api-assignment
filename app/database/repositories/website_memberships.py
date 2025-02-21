# website_membership.py (Website Membership Repository)

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncConnection
from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.website import WebsiteMembership


class WebsiteMembershipsRepository(BaseRepository):
    def __init__(self, conn: AsyncConnection) -> None:
        super().__init__(conn)

    @db_error_handler
    async def add_member(
        self, *, website_id: int, user_id: int, role: str
    ) -> WebsiteMembership:
        """Add a user to a website with a specific role."""
        membership = WebsiteMembership(
            website_id=website_id,
            user_id=user_id,
            role=role,
        )
        self.connection.add(membership)
        await self.connection.commit()
        await self.connection.refresh(membership)
        return membership

    @db_error_handler
    async def get_membership_by_id(
        self, *, membership_id: int
    ) -> WebsiteMembership | None:
        """Retrieve a website membership by its membership ID."""
        query = (
            select(WebsiteMembership)
            .where(WebsiteMembership.id == membership_id)
            .limit(1)
        )

        raw_result = await self.connection.execute(query)
        membership = raw_result.scalar_one_or_none()
        return membership

    @db_error_handler
    async def remove_member(self, *, membership_id: int) -> None:
        """Remove a website membership by membership_id."""
        query = WebsiteMembership.__table__.delete().where(
            WebsiteMembership.id == membership_id
        )
        await self.connection.execute(query)
        await self.connection.commit()

    @db_error_handler
    async def get_memberships_by_user(self, *, user_id: int) -> list[WebsiteMembership]:
        """Get all website memberships for a user."""
        query = select(WebsiteMembership).where(WebsiteMembership.user_id == user_id)
        raw_results = await self.connection.execute(query)
        return raw_results.scalars().all()

    @db_error_handler
    async def get_members_by_website(
        self, *, website_id: int
    ) -> list[WebsiteMembership]:
        """Get all members of a website."""
        query = select(WebsiteMembership).where(
            WebsiteMembership.website_id == website_id
        )
        raw_results = await self.connection.execute(query)
        return raw_results.scalars().all()

    @db_error_handler
    async def update_member_role(
        self, *, website_id: int, user_id: int, role: str
    ) -> WebsiteMembership:
        """Update a member's role in a website."""
        query = select(WebsiteMembership).where(
            and_(
                WebsiteMembership.website_id == website_id,
                WebsiteMembership.user_id == user_id,
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
        self, *, user_id: int, website_id: int
    ) -> WebsiteMembership:
        """Retrieve a membership record for a specific user and website."""
        query = (
            select(WebsiteMembership)
            .where(
                and_(
                    WebsiteMembership.website_id == website_id,
                    WebsiteMembership.user_id == user_id,
                )
            )
            .limit(1)
        )
        raw_result = await self.connection.execute(query)
        membership = raw_result.scalar_one_or_none()
        return membership
