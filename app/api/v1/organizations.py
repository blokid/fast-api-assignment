from fastapi import APIRouter, BackgroundTasks, Depends
from starlette.status import HTTP_200_OK

from app.api.dependencies.auth import get_current_user_auth
from app.api.dependencies.database import get_repository
from app.api.dependencies.service import get_service
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.database.repositories.organizations import OrganizationsRepository
from app.models.user import User
from app.schemas.organization import (
    OrganizationInCreate,
    OrganizationInviteIn,
    OrganizationResponse,
)
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


@router.get(
    "/{organization_id}",
    status_code=HTTP_200_OK,
    response_model=OrganizationResponse,
    responses=ERROR_RESPONSES,
    name="organization:info",
)
async def read_organization(
    *,
    user: User = Depends(get_current_user_auth()),
    organization_id: int,
    orgs_service: OrganizationsService = Depends(get_service(OrganizationsService)),
    orgs_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
):
    result = await orgs_service.get_organization(
        organization_id=organization_id,
        orgs_repo=orgs_repo,
        user=user,
    )

    return await handle_result(result)


@router.delete(
    "/{organization_id}",
    status_code=HTTP_200_OK,
    response_model=OrganizationResponse,
    responses=ERROR_RESPONSES,
    name="organization:delete",
)
async def delete_organization(
    *,
    user: User = Depends(get_current_user_auth()),
    organization_id: int,
    orgs_service: OrganizationsService = Depends(get_service(OrganizationsService)),
    orgs_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
):
    result = await orgs_service.delete_organization(
        organization_id=organization_id,
        orgs_repo=orgs_repo,
        user=user,
    )

    return await handle_result(result)


@router.post(
    "/{organization_id}/invite",
    status_code=HTTP_200_OK,
    response_model=OrganizationResponse,
    responses=ERROR_RESPONSES,
    name="organization:invite",
)
async def invite_to_organization(
    *,
    user: User = Depends(get_current_user_auth()),
    organization_id: int,
    background_tasks: BackgroundTasks,
    settings: AppSettings = Depends(get_app_settings),
    orgs_service: OrganizationsService = Depends(get_service(OrganizationsService)),
    orgs_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
    invite_in: OrganizationInviteIn,
):
    secret_key = str(settings.secret_key.get_secret_value())
    result = await orgs_service.invite_to_organization(
        organization_id=organization_id,
        background_tasks=background_tasks,
        secret_key=secret_key,
        invite_in=invite_in,
        orgs_repo=orgs_repo,
        user=user,
    )

    return await handle_result(result)
