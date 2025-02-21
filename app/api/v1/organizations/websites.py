# website_routes.py (Website Routes)

from fastapi import APIRouter, Depends, Path
from starlette.status import HTTP_200_OK, HTTP_201_CREATED
from app.api.dependencies.role_checker import (
    require_org_role,
    require_website_role,
    require_org_or_website_role,
)
from app.api.dependencies.auth import get_current_user_auth
from app.api.dependencies.database import get_repository
from app.api.dependencies.service import get_service
from app.api.dependencies.websites import get_websites_filters
from app.models.user import User
from app.models.website import Website, WebsiteRoleEnum
from app.models.organization import OrganizationRoleEnum
from app.database.repositories.websites import WebsitesRepository
from app.schemas.website import (
    WebsiteInUpdate,
    WebsiteResponse,
    WebsiteInCreate,
    WebsitesFilters,
)
from app.services.websites import WebsitesService
from app.utils import ERROR_RESPONSES, handle_result


router = APIRouter()


@router.get(
    "",
    status_code=HTTP_200_OK,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="websites:all-user-websites",
)
async def read_user_websites(
    user: User = Depends(get_current_user_auth()),
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
) -> WebsiteResponse:
    """Retrieve all websites that the user belongs to."""
    result = await websites_service.get_user_websites(
        user_id=user.id,
        websites_repo=websites_repo,
    )
    return await handle_result(result)


@router.get(
    "/{website_id}",
    status_code=HTTP_200_OK,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="website:info-by-id",
)
async def read_website_by_id(
    *,
    user: User = Depends(get_current_user_auth()),
    membership=Depends(
        require_org_or_website_role(
            [OrganizationRoleEnum.admin],
            [WebsiteRoleEnum.admin, WebsiteRoleEnum.member],
        )
    ),
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    website_id: int,
) -> WebsiteResponse:
    """Retrieve a website by its ID."""
    result = await websites_service.get_website_by_id(
        websites_repo=websites_repo,
        website_id=website_id,
    )
    return await handle_result(result)


@router.patch(
    "/{website_id}",
    status_code=HTTP_200_OK,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="website:update-by-id",
)
async def update_website(
    *,
    user: User = Depends(get_current_user_auth()),
    membership=Depends(
        require_org_or_website_role(
            [OrganizationRoleEnum.admin],
            [WebsiteRoleEnum.admin, WebsiteRoleEnum.member],
        )
    ),
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    website_id: int = Path(..., description="The website ID"),
    website_in: WebsiteInUpdate,
) -> WebsiteResponse:
    """Update a website by its ID."""
    result = await websites_service.update_website(
        website_id=website_id,
        website_in=website_in,
        websites_repo=websites_repo,
    )
    return await handle_result(result)
