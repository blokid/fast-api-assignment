import logging
from fastapi.encoders import jsonable_encoder
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from fastapi import Depends
from app.api.dependencies.database import get_repository
from app.database.repositories.organization_memberships import (
    OrganizationMembershipsRepository,
)
from app.models.organization import OrganizationMembership
from app.schemas.organization_membership import (
    OrganizationMembershipInCreate,
    OrganizationMembershipOutData,
)
from app.services.base import BaseService
from app.utils import ServiceResult, response_4xx, response_5xx, return_service

logger = logging.getLogger(__name__)


class OrganizationMembershipsService(BaseService):
    @return_service
    async def add_member(
        self,
        organization_id: int,
        membership_in: OrganizationMembershipInCreate,
        organization_memberships_repo: OrganizationMembershipsRepository,
    ) -> ServiceResult:
        try:
            created_membership: OrganizationMembership = (
                await organization_memberships_repo.add_member(
                    organization_id=organization_id,
                    user_id=membership_in.user_id,
                    role=membership_in.role,
                )
            )
        except Exception as e:
            logger.error(f"Error adding membership: {e}")
            return response_5xx(
                context={"reason": "Failed to add membership."},
            )

        membership_out = OrganizationMembershipOutData(
            organization_id=organization_id,
            id=created_membership.id,
            user_id=created_membership.user_id,
            role=created_membership.role,
            joined_at=created_membership.joined_at,
        )
        return dict(
            status_code=HTTP_201_CREATED,
            content={
                "message": "Organization membership created successfully.",
                "data": jsonable_encoder(membership_out),
            },
        )

    @return_service
    async def remove_member(
        self,
        membership_id: int,
        organization_memberships_repo: OrganizationMembershipsRepository,
    ) -> ServiceResult:
        """Remove a membership by membership_id."""
        try:
            await organization_memberships_repo.remove_member(
                membership_id=membership_id,
            )
        except Exception as e:
            logger.error(f"Error removing membership: {e}")
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": "Membership not found or could not be removed."},
            )

        return dict(
            status_code=HTTP_200_OK,
            content={"message": "Membership removed successfully."},
        )
