from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationInUpdate


class OrganizationsRepository(BaseRepository):
    def __init__(self, conn: AsyncConnection) -> None:
        super().__init__(conn)

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
