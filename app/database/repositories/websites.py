# website.py (Website Repository)

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import union_all
from app.models.organization import OrganizationMembership, Organization
from app.core.constant import FAIL_VALIDATION_WEBSITE_NOT_FOUND
from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.website import Website, WebsiteMembership
from app.schemas.website import (
    WebsiteInCreate,
    WebsiteInDB,
    WebsiteInUpdate,
)


class WebsitesRepository(BaseRepository):
    def __init__(self, conn: AsyncConnection) -> None:
        super().__init__(conn)

    @db_error_handler
    async def get_website_by_id(self, *, website_id: int) -> Website:
        query = (
            select(Website)
            .options(selectinload(Website.members))
            .where(and_(Website.id == website_id, Website.deleted_at.is_(None)))
        )
        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()
        return result.Website if result is not None else None

    @db_error_handler
    async def get_website_by_name(self, *, name: str) -> Website:
        query = select(Website).where(
            and_(Website.name == name, Website.deleted_at.is_(None))
        )
        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()
        return result.Website if result is not None else None

    @db_error_handler
    async def get_filtered_websites(
        self, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> list[Website]:
        query = (
            select(Website)
            .where(
                and_(
                    Website.organization_id == organization_id,
                    Website.deleted_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        raw_results = await self.connection.execute(query)
        results = raw_results.scalars().all()
        return results

    @db_error_handler
    async def create_website(
        self, *, website_in: WebsiteInCreate, organization_id: int
    ) -> Website:
        website_in_db_obj = WebsiteInDB(
            name=website_in.name,
            description=website_in.description,
            url=website_in.url,
            organization_id=organization_id,
        )
        created_website = Website(**website_in_db_obj.model_dump(exclude_none=True))
        self.connection.add(created_website)
        await self.connection.commit()
        await self.connection.refresh(created_website)
        return created_website

    @db_error_handler
    async def update_website(
        self, *, website: Website, website_in: WebsiteInUpdate
    ) -> Website:
        """Update an existing website with provided fields."""
        website_in_obj = website_in.model_dump(exclude_unset=True)

        for key, val in website_in_obj.items():
            setattr(website, key, val)

        self.connection.add(website)
        await self.connection.commit()
        await self.connection.refresh(website)

        return website

    @db_error_handler
    async def delete_website(self, *, organization_id: int, website_id: int) -> Website:
        query = select(Website).where(
            and_(
                Website.id == website_id,
                Website.organization_id == organization_id,
                Website.deleted_at.is_(None),
            )
        )
        raw_result = await self.connection.execute(query)
        website = raw_result.scalar_one_or_none()

        if not website:
            raise ValueError(FAIL_VALIDATION_WEBSITE_NOT_FOUND)
        website.deleted_at = func.now()
        self.connection.add(website)
        await self.connection.commit()
        await self.connection.refresh(website)
        return website

    @db_error_handler
    async def get_website_members(self, *, website_id: int) -> list[WebsiteMembership]:
        query = select(WebsiteMembership).where(
            WebsiteMembership.website_id == website_id
        )
        raw_results = await self.connection.execute(query)
        results = raw_results.scalars().all()
        return results

    @db_error_handler
    async def get_all_user_websites(self, *, user_id: int) -> list[Website]:
        """Get all websites the user belongs to (direct website or organization membership)."""

        # Query: Direct Website Memberships
        direct_results = await self.connection.execute(
            select(Website)
            .join(WebsiteMembership, WebsiteMembership.website_id == Website.id)
            .where(
                WebsiteMembership.user_id == user_id,
                Website.deleted_at.is_(None),
            )
        )
        direct_websites = direct_results.scalars().all()

        # Query: Organization-Based Website Memberships
        org_results = await self.connection.execute(
            select(Website)
            .join(Organization, Organization.id == Website.organization_id)
            .join(
                OrganizationMembership,
                OrganizationMembership.organization_id == Organization.id,
            )
            .where(
                OrganizationMembership.user_id == user_id,
                Website.deleted_at.is_(None),
            )
        )
        org_websites = org_results.scalars().all()

        # Merge and remove duplicates
        all_websites = {
            website.id: website for website in direct_websites + org_websites
        }

        return list(all_websites.values())
