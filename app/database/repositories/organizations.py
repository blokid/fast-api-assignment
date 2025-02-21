from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database.repositories.base import BaseRepository, db_error_handler
from app.models.organization import Organization, OrganizationMembership
from app.schemas.organization import (
    OrganizationInCreate,
    OrganizationInDB,
    OrganizationInUpdate,
)


class OrganizationsRepository(BaseRepository):
    def __init__(self, conn: AsyncConnection) -> None:
        super().__init__(conn)

    @db_error_handler
    async def get_organization_by_id(self, *, organization_id: int) -> Organization:
        query = (
            select(Organization)
            .options(selectinload(Organization.members))
            .where(
                Organization.id == organization_id, Organization.deleted_at.is_(None)
            )
        )
        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()
        return result.Organization if result is not None else None

    @db_error_handler
    async def get_organization_by_name(self, *, name: str) -> Organization:
        query = select(Organization).where(
            and_(Organization.name == name, Organization.deleted_at.is_(None))
        )
        raw_result = await self.connection.execute(query)
        result = raw_result.fetchone()
        return result.Organization if result is not None else None

    @db_error_handler
    async def get_filtered_organizations(
        self, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Organization]:
        from app.models.organization import (
            OrganizationMembership,
        )  # Import here if needed

        query = (
            select(Organization)
            .join(
                Organization.members
            )  # joins on OrganizationMembership using relationship 'members'
            .where(
                OrganizationMembership.user_id == user_id,
                Organization.deleted_at.is_(None),
            )
            .offset(skip)
            .limit(limit)
        )
        raw_results = await self.connection.execute(query)
        results = raw_results.scalars().all()
        return results

    @db_error_handler
    async def create_organization(
        self, *, organization_in: OrganizationInCreate
    ) -> Organization:
        organization_in_db_obj = OrganizationInDB(
            name=organization_in.name,
            description=organization_in.description,
        )
        created_organization = Organization(
            **organization_in_db_obj.model_dump(exclude_none=True)
        )
        self.connection.add(created_organization)
        await self.connection.commit()
        await self.connection.refresh(created_organization)
        return created_organization

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
    async def delete_organization_by_id(self, *, organization_id: int) -> None:
        """Soft-delete an organization by organization_id."""
        query = (
            Organization.__table__.update()
            .where(Organization.id == organization_id)
            .values(deleted_at=func.now())
        )
        await self.connection.execute(query)
        await self.connection.commit()

    @db_error_handler
    async def add_organization_member(
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
    async def remove_organization_member(
        self, *, organization_id: int, user_id: int
    ) -> None:
        query = OrganizationMembership.__table__.delete().where(
            and_(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.user_id == user_id,
            )
        )
        await self.connection.execute(query)
        await self.connection.commit()

    @db_error_handler
    async def get_organization_members(
        self, *, organization_id: int
    ) -> list[OrganizationMembership]:
        query = select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id
        )
        raw_results = await self.connection.execute(query)
        results = raw_results.scalars().all()
        return results
