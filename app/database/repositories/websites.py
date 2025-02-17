from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core import constant
from app.database.repositories.base import BaseRepository, db_error_handler
from app.models import Organization, User, Website, WebsiteInvite, WebsiteUser
from app.schemas.website import WebsiteInCreate, WebsiteInUpdate


class WebsitesRepository(BaseRepository):
    def __init__(self, conn: AsyncConnection) -> None:
        super().__init__(conn)

    @db_error_handler
    async def create_website(
        self, *, website_in: WebsiteInCreate, user: User, organization: Organization
    ) -> Website:
        website = Website(**website_in.model_dump())
        website.users.append(WebsiteUser(role=constant.WEBSITE_ADMIN, user=user))
        org_websites = await organization.awaitable_attrs.websites
        org_websites.append(website)
        self.connection.add(website)
        await self.connection.commit()
        await self.connection.refresh(website)
        return website

    @db_error_handler
    async def get_websites(self) -> list[Website]:
        query = select(Website).where(Website.deleted_at.is_(None))
        raw_results = await self.connection.execute(query)
        results = raw_results.scalars().all()
        return results

    @db_error_handler
    async def get_website_by_id(self, *, website_id: int) -> Website:
        query = select(Website).where(Website.id == website_id).limit(1)

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

        return result.Website if result is not None else result

    @db_error_handler
    async def get_website_by_name(self, *, name: str) -> Website:
        query = select(Website).where(Website.name == name).limit(1)

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

        return result.Website if result is not None else result

    @db_error_handler
    async def get_duplicate_website(self, *, website_in: WebsiteInCreate) -> Website:
        query = (
            select(Website)
            .where(or_(Website.name == website_in.name, Website.url == website_in.url))
            .limit(1)
        )
        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()
        return result.Website if result is not None else result

    @db_error_handler
    async def get_websites_by_user_id(self, *, user_id: int) -> list[Website]:
        query = select(Website).join(Website.users).where(User.id == user_id)
        raw_results = await self.connection.execute(query)
        results = raw_results.scalars().all()
        return results

    @db_error_handler
    async def update_website(
        self, *, website: Website, website_in: WebsiteInUpdate
    ) -> Website:
        website_in_obj = website_in.model_dump(exclude_unset=True)
        for key, val in website_in_obj.items():
            setattr(website, key, val)

        self.connection.add(website)
        await self.connection.commit()
        await self.connection.refresh(website)
        return website

    @db_error_handler
    async def delete_website(self, *, website: Website) -> Website:
        website.deleted_at = func.now()
        self.connection.add(website)
        await self.connection.commit()
        await self.connection.refresh(website)
        return website

    @db_error_handler
    async def invite_to_website(
        self, *, website: Website, email: str, role: str
    ) -> WebsiteInvite:
        invite = WebsiteInvite(email=email, role=role)
        website_invites = await website.awaitable_attrs.invites
        website_invites.append(invite)
        self.connection.add(website)
        await self.connection.commit()
        await self.connection.refresh(website)
        return invite

    @db_error_handler
    async def delete_website_invite(self, *, invite: WebsiteInvite) -> WebsiteInvite:
        invite.deleted_at = func.now()
        self.connection.add(invite)
        await self.connection.commit()
        await self.connection.refresh(invite)
        return invite

    @db_error_handler
    async def get_website_invite(self, *, website_id: int, email: str) -> WebsiteInvite:
        query = (
            select(WebsiteInvite)
            .where(
                and_(
                    WebsiteInvite.website_id == website_id,
                    WebsiteInvite.email == email,
                )
            )
            .limit(1)
        )
        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()
        return result.WebsiteInvite if result is not None else result

    @db_error_handler
    async def accept_website_invite(self, *, org_invite: WebsiteInvite, user: User):
        org_invite.is_accepted = True
        self.connection.add(org_invite)
        website: Website = await org_invite.awaitable_attrs.website
        users = await website.awaitable_attrs.users
        users.append(WebsiteUser(role=org_invite.role, user=user))
        self.connection.add(website)
        await self.connection.commit()
        await self.connection.refresh(org_invite)
        await self.connection.refresh(website)
        return org_invite

    @db_error_handler
    async def get_website_users(self, *, website_id: int):
        query = select(WebsiteUser).where(WebsiteUser.website_id == website_id)
        raw_results = await self.connection.execute(query)
        results = raw_results.scalars().all()
        return results
