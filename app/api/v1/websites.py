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
    OrganizationResponse,
)
from app.schemas.organization_user import OrganizationUserResponse
from app.schemas.user import InvitationTokenData
from app.schemas.website import (
    WebsiteInCreate,
    WebsiteInUpdate,
    WebsiteInviteIn,
    WebsiteResponse,
)
from app.schemas.website_user import WebsiteUserResponse
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
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
) -> ServiceResult:
    """
    Read all websites.
    """
    result = await websites_service.get_websites(
        websites_repo=websites_repo,
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
    "/{website_id}",
    status_code=HTTP_200_OK,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="website:info",
)
async def read_website(
    *,
    user: User = Depends(get_current_user_auth()),
    website_id: int,
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
) -> ServiceResult:
    """
    Read website info.
    """
    result = await websites_service.get_website(
        website_id=website_id,
        websites_repo=websites_repo,
        user=user,
    )

    return await handle_result(result)


@router.delete(
    "/{website_id}",
    status_code=HTTP_200_OK,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="website:delete",
)
async def delete_website(
    *,
    user: User = Depends(get_current_user_auth()),
    website_id: int,
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
) -> ServiceResult:
    """
    Delete website.
    """
    result = await websites_service.delete_website(
        website_id=website_id,
        websites_repo=websites_repo,
        user=user,
    )

    return await handle_result(result)


@router.post(
    "/{website_id}/invite",
    status_code=HTTP_200_OK,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="website:invite",
)
async def invite_to_website(
    *,
    user: User = Depends(get_current_user_auth()),
    website_id: int,
    background_tasks: BackgroundTasks,
    settings: AppSettings = Depends(get_app_settings),
    orgs_service: OrganizationsService = Depends(get_service(OrganizationsService)),
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    orgs_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    invite_in: WebsiteInviteIn,
) -> ServiceResult:
    """
    Invite user to website.
    """
    secret_key = str(settings.secret_key.get_secret_value())
    result = await websites_service.invite_to_website(
        website_id=website_id,
        background_tasks=background_tasks,
        secret_key=secret_key,
        invite_in=invite_in,
        websites_repo=websites_repo,
        user=user,
    )

    return await handle_result(result)


@router.post(
    "/accept-invite",
    status_code=HTTP_200_OK,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="website:accept-invite",
)
async def accept_website_invite(
    *,
    user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    token: InvitationTokenData,
    settings: AppSettings = Depends(get_app_settings),
) -> ServiceResult:
    """
    Accept website invite.
    """
    secret_key = str(settings.secret_key.get_secret_value())
    result = await websites_service.accept_website_invite(
        token_in=token,
        websites_repo=websites_repo,
        user_repo=user_repo,
        secret_key=secret_key,
    )
    return await handle_result(result)


@router.get(
    "/{website_id}/users",
    status_code=HTTP_200_OK,
    response_model=WebsiteUserResponse,
    responses=ERROR_RESPONSES,
    name="website:users",
)
async def get_website_users(
    *,
    user: User = Depends(get_current_user_auth()),
    website_id: int,
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
) -> ServiceResult:
    """
    Get website users.
    """
    result = await websites_service.get_website_users(
        website_id=website_id,
        websites_repo=websites_repo,
        user=user,
    )
    return await handle_result(result)


@router.patch(
    "/{website_id}",
    status_code=HTTP_200_OK,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="website:update",
)
async def update_website(
    *,
    user: User = Depends(get_current_user_auth()),
    website_id: int,
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    website_in: WebsiteInUpdate,
) -> ServiceResult:
    """
    Update website.
    """
    result = await websites_service.update_website(
        website_id=website_id,
        websites_repo=websites_repo,
        user=user,
        website_in=website_in,
    )

    return await handle_result(result)
