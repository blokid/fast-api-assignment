import logging

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.api.dependencies.database import get_repository
from app.core import constant
from app.database.repositories.organizations import OrganizationsRepository
from app.models.user import User
from app.schemas.organization import (
    OrganizationInCreate,
    OrganizationOutData,
    OrganizationResponse,
)
from app.services.base import BaseService
from app.utils import (
    response_4xx,
    return_service,
)

logger = logging.getLogger(__name__)


class OrganizationsService(BaseService):

    @return_service
    async def create_organization(
        self,
        org_in: OrganizationInCreate,
        user: User,
        orgs_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> OrganizationResponse:
        duplicate_org = await orgs_repo.get_organization_by_name(name=org_in.name)

        if duplicate_org:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": constant.FAIL_VALIDATION_ORGANIZATION_DUPLICATED},
            )

        created_org = await orgs_repo.create_organization(org_in=org_in, user=user)

        return dict(
            status_code=HTTP_201_CREATED,
            content={
                "message": constant.SUCCESS_CREATE_ORGANIZATION,
                "data": jsonable_encoder(
                    OrganizationOutData.model_validate(created_org)
                ),
            },
        )

    @return_service
    async def get_organizations(
        self,
        orgs_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> OrganizationResponse:
        organizations = await orgs_repo.get_organizations()

        if not organizations:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NO_ORGANIZATION},
            )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_GET_ORGANIZATION,
                "data": jsonable_encoder(
                    [OrganizationOutData.model_validate(org) for org in organizations]
                ),
            },
        )
