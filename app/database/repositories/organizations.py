from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core import constant
from app.database.repositories.base import BaseRepository, db_error_handler
from app.models import Organization, OrganizationInvite, OrganizationUser, User
from app.schemas.organization import OrganizationInCreate, OrganizationInUpdate


class OrganizationsRepository(BaseRepository):
    def __init__(self, conn: AsyncConnection) -> None:
        super().__init__(conn)

    @db_error_handler
    async def create_organization(
        self, *, org_in: OrganizationInCreate, user: User
    ) -> Organization:
        organization = Organization(**org_in.model_dump())
        organization.users.append(
            OrganizationUser(role=constant.ORGANIZATION_ADMIN, user=user)
        )
        self.connection.add(organization)
        await self.connection.commit()
        await self.connection.refresh(organization)
        return organization

    @db_error_handler
    async def get_organizations(self) -> list[Organization]:
        query = select(Organization).where(Organization.deleted_at.is_(None))
        raw_results = await self.connection.execute(query)
        results = raw_results.scalars().all()
        return results

    @db_error_handler
    async def get_organization_by_id(self, *, organization_id: int) -> Organization:
        query = select(Organization).where(Organization.id == organization_id).limit(1)

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

        return result.Organization if result is not None else result

    @db_error_handler
    async def get_organization_by_name(self, *, name: str) -> Organization:
        query = select(Organization).where(Organization.name == name).limit(1)

        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()

        return result.Organization if result is not None else result

    @db_error_handler
    async def get_organizations_by_user_id(self, *, user_id: int) -> list[Organization]:
        query = select(Organization).join(Organization.users).where(User.id == user_id)
        raw_results = await self.connection.execute(query)
        results = raw_results.scalars().all()
        return results

    @db_error_handler
    async def update_organization(
        self, *, organization: Organization, organization_in: OrganizationInUpdate
    ) -> Organization:
        organization_in_obj = organization_in.model_dump(exclude_unset=True)
        for key, val in organization_in_obj.items():
            setattr(organization, key, val)

        self.connection.add(organization)
        await self.connection.commit()
        await self.connection.refresh(organization)
        return organization

    @db_error_handler
    async def delete_organization(self, *, organization: Organization) -> Organization:
        organization.deleted_at = func.now()
        self.connection.add(organization)
        await self.connection.commit()
        await self.connection.refresh(organization)
        return organization

    @db_error_handler
    async def invite_to_organization(
        self, *, organization: Organization, email: str, role: str
    ) -> OrganizationInvite:
        invite = OrganizationInvite(email=email, role=role)
        org_invites = await organization.awaitable_attrs.invites
        org_invites.append(invite)
        self.connection.add(organization)
        await self.connection.commit()
        await self.connection.refresh(organization)
        return invite

    @db_error_handler
    async def delete_organization_invite(
        self, *, invite: OrganizationInvite
    ) -> OrganizationInvite:
        invite.deleted_at = func.now()
        self.connection.add(invite)
        await self.connection.commit()
        await self.connection.refresh(invite)
        return invite

    @db_error_handler
    async def get_organization_invite(
        self, *, organization_id: int, email: str
    ) -> OrganizationInvite:
        query = (
            select(OrganizationInvite)
            .where(
                and_(
                    OrganizationInvite.organization_id == organization_id,
                    OrganizationInvite.email == email,
                )
            )
            .limit(1)
        )
        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()
        return result.OrganizationInvite if result is not None else result

    @db_error_handler
    async def accept_organization_invite(
        self, *, org_invite: OrganizationInvite, user: User
    ):
        org_invite.is_accepted = True
        self.connection.add(org_invite)
        organization: Organization = await org_invite.awaitable_attrs.organization
        users = await organization.awaitable_attrs.users
        users.append(OrganizationUser(role=org_invite.role, user=user))
        self.connection.add(organization)
        await self.connection.commit()
        await self.connection.refresh(org_invite)
        await self.connection.refresh(organization)
        return org_invite
