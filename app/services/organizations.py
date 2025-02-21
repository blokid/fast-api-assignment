import logging
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from app.api.dependencies.database import get_repository
from app.core import constant
from app.api.dependencies.organizations import get_organizations_filters
from app.database.repositories.organizations import OrganizationsRepository
from app.models.organization import Organization
from app.schemas.organization import (
    OrganizationInCreate,
    OrganizationDetailOut,
    OrganizationInDB,
    OrganizationsFilters,
    OrganizationOutData,
    MembershipOutData,
    OrganizationInUpdate,
)
from app.services.base import BaseService
from app.utils import ServiceResult, response_4xx, return_service

logger = logging.getLogger(__name__)


class OrganizationsService(BaseService):
    @return_service
    async def get_organizations(
        self,
        user_id: str,
        organizations_filters: OrganizationsFilters = Depends(
            get_organizations_filters
        ),
        organizations_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> ServiceResult:
        organizations = await organizations_repo.get_filtered_organizations(
            skip=organizations_filters.skip,
            limit=organizations_filters.limit,
            user_id=user_id,
        )

        if not organizations:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={
                    "reason": constant.FAIL_VALIDATION_MATCHED_FILTERED_ORGANIZATIONS
                },
            )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_GET_ORGANIZATIONS,
                "data": jsonable_encoder(
                    [
                        OrganizationOutData.model_validate(org.__dict__)
                        for org in organizations
                    ]
                ),
            },
        )

    @return_service
    async def create_organization(
        self,
        organization_in: OrganizationInCreate,
        organizations_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> ServiceResult:
        created_organization = await organizations_repo.create_organization(
            organization_in=organization_in
        )
        return (
            dict(
                status_code=HTTP_201_CREATED,
                content=jsonable_encoder(
                    OrganizationInDB.model_validate(created_organization.__dict__)
                ),
            ),
            created_organization.__dict__,
        )

    @return_service
    async def get_organization_by_id(
        self,
        organization_id: int,
        organizations_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> ServiceResult:
        organization = await organizations_repo.get_organization_by_id(
            organization_id=organization_id
        )
        if not organization:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_VALIDATION_ORGANIZATION_NOT_FOUND},
            )

        members = [
            MembershipOutData.model_validate(member.__dict__)
            for member in organization.members
        ]

        org_data = OrganizationDetailOut.model_validate(
            {**organization.__dict__, "members": members}
        )

        return dict(
            status_code=HTTP_200_OK,
            content={"data": jsonable_encoder(org_data)},
        )

    @return_service
    async def update_organization(
        self,
        organization_id: int,
        organization_in: OrganizationInUpdate,
        organizations_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> ServiceResult:
        organization = await organizations_repo.get_organization_by_id(
            organization_id=organization_id
        )
        if not organization:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_VALIDATION_ORGANIZATION_NOT_FOUND},
            )

        updated_organization = await organizations_repo.update_organization(
            organization=organization,
            organization_in=organization_in,
        )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_UPDATE_ORGANIZATION,
                "data": jsonable_encoder(
                    OrganizationInDB.model_validate(updated_organization.__dict__)
                ),
            },
        )

    @return_service
    async def delete_organization(
        self,
        organization_id: int,
        organizations_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> ServiceResult:
        # Retrieve the organization
        organization = await organizations_repo.get_organization_by_id(
            organization_id=organization_id
        )
        if not organization:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_VALIDATION_ORGANIZATION_NOT_FOUND},
            )

        # Delete the organization
        await organizations_repo.delete_organization_by_id(
            organization_id=organization_id
        )

        return dict(
            status_code=HTTP_200_OK,
            content={"message": constant.SUCCESS_DELETE_ORGANIZATION},
        )
