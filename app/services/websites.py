# website_service.py (Website Service)

import logging
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from app.api.dependencies.database import get_repository
from app.core import constant
from app.api.dependencies.websites import get_websites_filters
from app.database.repositories.websites import WebsitesRepository
from app.models.website import Website
from app.schemas.website import (
    WebsiteInCreate,
    WebsiteDetailOut,
    WebsiteInDB,
    WebsitesFilters,
    WebsiteOutData,
    WebsiteInUpdate,
)
from app.schemas.website_membership import WebsiteMembershipOutData
from app.services.base import BaseService
from app.utils import ServiceResult, response_4xx, return_service

logger = logging.getLogger(__name__)


class WebsitesService(BaseService):
    @return_service
    async def get_websites(
        self,
        organization_id: str,
        websites_filters: WebsitesFilters = Depends(get_websites_filters),
        websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    ) -> ServiceResult:
        """Retrieve websites filtered by user and query parameters."""
        websites = await websites_repo.get_filtered_websites(
            skip=websites_filters.skip,
            limit=websites_filters.limit,
            organization_id=organization_id,
        )

        if not websites:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_VALIDATION_MATCHED_FILTERED_WEBSITES},
            )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_GET_WEBSITES,
                "data": jsonable_encoder(
                    [
                        WebsiteOutData.model_validate(website.__dict__)
                        for website in websites
                    ]
                ),
            },
        )

    @return_service
    async def get_user_websites(
        self,
        user_id: int,
        websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    ) -> ServiceResult:
        """Get all websites that the user belongs to via website or organization memberships."""

        websites = await websites_repo.get_all_user_websites(user_id=user_id)

        if not websites:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_VALIDATION_MATCHED_FILTERED_WEBSITES},
            )

        return {
            "status_code": HTTP_200_OK,
            "content": {
                "message": constant.SUCCESS_GET_WEBSITES,
                "data": jsonable_encoder(
                    [
                        WebsiteOutData.model_validate(website.__dict__)
                        for website in websites
                    ]
                ),
            },
        }

    @return_service
    async def create_website(
        self,
        website_in: WebsiteInCreate,
        organization_id: int,
        websites_repo: WebsitesRepository,
    ) -> ServiceResult:
        """Create a new website."""
        created_website = await websites_repo.create_website(
            website_in=website_in,
            organization_id=organization_id,
        )

        return {
            "status_code": HTTP_201_CREATED,
            "content": {
                "message": "Website created successfully.",
                "data": jsonable_encoder(
                    WebsiteInDB.model_validate(created_website.__dict__)
                ),
            },
        }

    @return_service
    async def get_website_by_id(
        self,
        website_id: int,
        websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    ) -> ServiceResult:
        """Get website details by ID, including members."""
        website = await websites_repo.get_website_by_id(website_id=website_id)
        if not website:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_VALIDATION_WEBSITE_NOT_FOUND},
            )

        members = [
            WebsiteMembershipOutData.model_validate(member.__dict__)
            for member in website.members
        ]

        website_data = WebsiteDetailOut.model_validate(
            {**website.__dict__, "members": members}
        )

        return dict(
            status_code=HTTP_200_OK,
            content={"data": jsonable_encoder(website_data)},
        )

    @return_service
    async def update_website(
        self,
        website_id: int,
        website_in: WebsiteInUpdate,
        websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    ) -> ServiceResult:

        website = await websites_repo.get_website_by_id(website_id=website_id)
        if not website:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_VALIDATION_WEBSITE_NOT_FOUND},
            )

        updated_website = await websites_repo.update_website(
            website=website,
            website_in=website_in,
        )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_UPDATE_WEBSITE,
                "data": jsonable_encoder(
                    WebsiteInDB.model_validate(updated_website.__dict__)
                ),
            },
        )

    @return_service
    async def delete_website(
        self,
        *,
        organization_id: int,
        website_id: int,
        websites_repo: WebsitesRepository,
    ) -> ServiceResult:
        """Delete a website by its ID under the organization."""
        try:
            deleted_website = await websites_repo.delete_website(
                organization_id=organization_id,
                website_id=website_id,
            )
            return {
                "status_code": HTTP_200_OK,
                "content": {
                    "message": constant.SUCCESS_DELETE_WEBSITE,
                    "data": jsonable_encoder(
                        WebsiteInDB.model_validate(deleted_website.__dict__)
                    ),
                },
            }
        except ValueError as e:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": str(e)},
            )
        except Exception as e:
            logger.error(f"Error deleting website: {e}")
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_VALIDATION_WEBSITE_DELETION_FAILED},
            )
