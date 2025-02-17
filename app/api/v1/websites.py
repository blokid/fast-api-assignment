from fastapi import APIRouter, BackgroundTasks, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.api.dependencies.auth import get_current_user_auth
from app.api.dependencies.database import get_repository
from app.api.dependencies.service import get_service
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.database.repositories.organizations import OrganizationsRepository
from app.database.repositories.users import UsersRepository
from app.database.repositories.websites import WebsitesRepository
from app.models.user import User
from app.schemas.organization import (
    OrganizationInCreate,
    OrganizationInviteIn,
    OrganizationResponse,
)
from app.schemas.organization_user import OrganizationUserResponse
from app.schemas.user import InvitationTokenData
from app.schemas.website import (
    WebsiteInCreate,
    WebsiteInUpdate,
    WebsiteResponse,
)
from app.services.organizations import OrganizationsService
from app.services.websites import WebsitesService
from app.utils import ERROR_RESPONSES, ServiceResult, handle_result

router = APIRouter()


@router.get(
    "",
    status_code=HTTP_200_OK,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="websites:all",
)
async def read_websites(
    *,
    website_service: WebsitesService = Depends(get_service(WebsitesService)),
    website_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
) -> ServiceResult:
    """
    Read all websites.
    """
    result = await website_service.get_websites(
        website_repo=website_repo,
    )

    return await handle_result(result)


@router.post(
    "",
    status_code=HTTP_201_CREATED,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="website:create",
)
async def create_website(
    *,
    organization_id: int,
    user: User = Depends(get_current_user_auth()),
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    orgs_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
    website_in: WebsiteInCreate,
) -> ServiceResult:
    """
    Create new website.
    """
    result = await websites_service.create_website(
        website_in=website_in,
        websites_repo=websites_repo,
        orgs_repo=orgs_repo,
        user=user,
        organization_id=organization_id,
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
) -> ServiceResult:
    """
    Read organization info.
    """
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
) -> ServiceResult:
    """
    Delete organization.
    """
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
) -> ServiceResult:
    """
    Invite user to organization.
    """
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


@router.post(
    "/accept-invite",
    status_code=HTTP_200_OK,
    response_model=OrganizationResponse,
    responses=ERROR_RESPONSES,
    name="organization:accept-invite",
)
async def accept_organization_invite(
    *,
    user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    orgs_service: OrganizationsService = Depends(get_service(OrganizationsService)),
    orgs_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
    token: InvitationTokenData,
    settings: AppSettings = Depends(get_app_settings),
) -> ServiceResult:
    """
    Accept organization invite.
    """
    secret_key = str(settings.secret_key.get_secret_value())
    result = await orgs_service.accept_organization_invite(
        token_in=token,
        orgs_repo=orgs_repo,
        user_repo=user_repo,
        secret_key=secret_key,
    )
    return await handle_result(result)


@router.get(
    "/{organization_id}/users",
    status_code=HTTP_200_OK,
    response_model=OrganizationUserResponse,
    responses=ERROR_RESPONSES,
    name="organization:users",
)
async def get_organization_users(
    *,
    user: User = Depends(get_current_user_auth()),
    organization_id: int,
    orgs_service: OrganizationsService = Depends(get_service(OrganizationsService)),
    orgs_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
) -> ServiceResult:
    """
    Get organization users.
    """
    result = await orgs_service.get_organization_users(
        organization_id=organization_id,
        orgs_repo=orgs_repo,
        user=user,
    )
    return await handle_result(result)
