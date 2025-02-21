# website_memberships_service.py (Website Membership Service)

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
from app.database.repositories.website_memberships import (
    WebsiteMembershipsRepository,
)
from app.models.website import WebsiteMembership
from app.schemas.website_membership import (
    WebsiteMembershipInCreate,
    WebsiteMembershipOutData,
)
from app.services.base import BaseService
from app.utils import ServiceResult, response_4xx, response_5xx, return_service

logger = logging.getLogger(__name__)


class WebsiteMembershipsService(BaseService):
    @return_service
    async def add_member(
        self,
        website_id: int,
        membership_in: WebsiteMembershipInCreate,
        website_memberships_repo: WebsiteMembershipsRepository = Depends(
            get_repository(WebsiteMembershipsRepository)
        ),
    ) -> ServiceResult:
        """Add a user to a website with a specific role."""
        try:
            created_membership: WebsiteMembership = (
                await website_memberships_repo.add_member(
                    website_id=website_id,
                    user_id=membership_in.user_id,
                    role=membership_in.role,
                )
            )
        except Exception as e:
            logger.error(f"Error adding website membership: {e}")
            return response_5xx(
                context={"reason": "Failed to add website membership."},
            )

        membership_out = WebsiteMembershipOutData(
            website_id=website_id,
            id=created_membership.id,
            user_id=created_membership.user_id,
            role=created_membership.role,
            joined_at=created_membership.joined_at,
        )
        return dict(
            status_code=HTTP_201_CREATED,
            content={
                "message": "Website membership created successfully.",
                "data": jsonable_encoder(membership_out),
            },
        )

    @return_service
    async def remove_member(
        self,
        membership_id: int,
        website_memberships_repo: WebsiteMembershipsRepository = Depends(
            get_repository(WebsiteMembershipsRepository)
        ),
    ) -> ServiceResult:

        try:
            membership = await website_memberships_repo.get_membership_by_id(
                membership_id=membership_id
            )
            if not membership:
                return response_4xx(
                    status_code=HTTP_404_NOT_FOUND,
                    context={
                        "reason": "Website membership not found with the provided ID."
                    },
                )

            await website_memberships_repo.remove_member(
                membership_id=membership_id,
            )
        except Exception as e:
            logger.error(f"Error removing website membership: {e}")
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={
                    "reason": "Website membership not found or could not be removed."
                },
            )

        return dict(
            status_code=HTTP_200_OK,
            content={"message": "Website membership removed successfully."},
        )
