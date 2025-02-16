from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK

from app.api.dependencies.auth import get_current_user_auth
from app.api.dependencies.database import get_repository
from app.api.dependencies.service import get_service
from app.database.repositories.organizations import OrganizationsRepository
from app.models.user import User
from app.schemas.organization import OrganizationInCreate, OrganizationResponse
from app.services.organizations import OrganizationsService
from app.utils import ERROR_RESPONSES, handle_result

router = APIRouter()


@router.get(
    "",
    status_code=HTTP_200_OK,
    response_model=OrganizationResponse,
    responses=ERROR_RESPONSES,
    name="organizations:all",
)
async def read_organizations(
    *,
    orgs_service: OrganizationsService = Depends(get_service(OrganizationsService)),
    orgs_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
):
    result = await orgs_service.get_organizations(
        orgs_repo=orgs_repo,
    )

    return await handle_result(result)


@router.post(
    "",
    status_code=HTTP_200_OK,
    response_model=OrganizationResponse,
    responses=ERROR_RESPONSES,
    name="organization:create",
)
async def create_organization(
    *,
    user: User = Depends(get_current_user_auth()),
    orgs_service: OrganizationsService = Depends(get_service(OrganizationsService)),
    orgs_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
    org_in: OrganizationInCreate,
) -> OrganizationResponse:
    result = await orgs_service.create_organization(
        org_in=org_in,
        orgs_repo=orgs_repo,
        user=user,
    )

    return await handle_result(result)
