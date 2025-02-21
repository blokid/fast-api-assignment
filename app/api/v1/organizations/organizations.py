from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED
from app.api.dependencies.role_checker import (
    require_org_role,
    require_org_or_website_role,
)
from app.api.dependencies.auth import get_current_user_auth
from app.api.dependencies.database import get_repository
from app.api.dependencies.service import get_service
from app.models.user import User
from app.api.dependencies.websites import get_websites_filters
from app.api.dependencies.organizations import get_organizations_filters
from app.database.repositories.organizations import OrganizationsRepository
from app.models.organization import Organization, OrganizationRoleEnum
from app.models.website import WebsiteRoleEnum
from app.schemas.organization import (
    OrganizationInUpdate,
    OrganizationResponse,
    OrganizationsFilters,
)
from app.services.organizations import OrganizationsService
from app.utils import ERROR_RESPONSES, handle_result
from app.database.repositories.websites import WebsitesRepository
from app.schemas.website import (
    WebsiteInUpdate,
    WebsiteResponse,
    WebsiteInCreate,
    WebsitesFilters,
)
from app.services.websites import WebsitesService

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
    user: User = Depends(get_current_user_auth()),
    organizations_service: OrganizationsService = Depends(
        get_service(OrganizationsService)
    ),
    organizations_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
    organizations_filters: OrganizationsFilters = Depends(get_organizations_filters),
):
    result = await organizations_service.get_organizations(
        user_id=user.id,
        organizations_repo=organizations_repo,
        organizations_filters=organizations_filters,
    )
    return await handle_result(result)


@router.get(
    "/{organization_id}",
    status_code=HTTP_200_OK,
    response_model=OrganizationResponse,
    responses=ERROR_RESPONSES,
    name="organization:info-by-id",
)
async def read_organization_by_id(
    *,
    user: User = Depends(get_current_user_auth()),
    membership=Depends(
        require_org_role([OrganizationRoleEnum.admin, OrganizationRoleEnum.member])
    ),
    organizations_service: OrganizationsService = Depends(
        get_service(OrganizationsService)
    ),
    organizations_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
    organization_id: int,
) -> OrganizationResponse:
    result = await organizations_service.get_organization_by_id(
        organizations_repo=organizations_repo,
        organization_id=organization_id,
    )
    return await handle_result(result)


@router.patch(
    "/{organization_id}",
    status_code=HTTP_200_OK,
    response_model=OrganizationResponse,
    responses=ERROR_RESPONSES,
    name="organization:patch-by-id",
)
async def update_organization(
    *,
    user: User = Depends(get_current_user_auth()),
    membership=Depends(
        require_org_role([OrganizationRoleEnum.admin, OrganizationRoleEnum.member])
    ),
    organizations_service: OrganizationsService = Depends(
        get_service(OrganizationsService)
    ),
    organizations_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
    organization_id: int,
    organization_in: OrganizationInUpdate,
) -> OrganizationResponse:
    result = await organizations_service.update_organization(
        organization_id=organization_id,
        organizations_repo=organizations_repo,
        organization_in=organization_in,
    )
    return await handle_result(result)


@require_org_role([OrganizationRoleEnum.admin])
@router.delete(
    "/{organization_id}",
    status_code=HTTP_200_OK,
    response_model=OrganizationResponse,
    responses=ERROR_RESPONSES,
    name="organization:delete-by-id",
)
async def delete_organization(
    *,
    organizations_service: OrganizationsService = Depends(
        get_service(OrganizationsService)
    ),
    organizations_repo: OrganizationsRepository = Depends(
        get_repository(OrganizationsRepository)
    ),
    token_user: Organization = Depends(get_current_user_auth()),
    organization_id: int,
) -> OrganizationResponse:
    result = await organizations_service.delete_organization(
        organizations_repo=organizations_repo,
        organization_id=organization_id,
    )
    return await handle_result(result)


@router.get(
    "/{organization_id}/websites",
    status_code=HTTP_200_OK,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="websites:all",
)
async def read_websites(
    *,
    user: User = Depends(get_current_user_auth()),
    membership=Depends(
        require_org_role([OrganizationRoleEnum.admin, OrganizationRoleEnum.member])
    ),
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    websites_filters: WebsitesFilters = Depends(get_websites_filters),
    organization_id: int,
):
    """Retrieve all websites with filters."""
    result = await websites_service.get_websites(
        organization_id=organization_id,
        websites_repo=websites_repo,
        websites_filters=websites_filters,
    )
    return await handle_result(result)


@router.delete(
    "/{organization_id}/websites/{website_id}",
    status_code=HTTP_200_OK,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="website:delete-by-id",
)
async def delete_website(
    *,
    membership=Depends(
        require_org_or_website_role(
            [OrganizationRoleEnum.admin], [WebsiteRoleEnum.admin]
        )
    ),
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    organization_id: int,
    website_id: int,
) -> WebsiteResponse:
    """Delete a website by its ID."""
    result = await websites_service.delete_website(
        organization_id=organization_id,
        websites_repo=websites_repo,
        website_id=website_id,
    )
    return await handle_result(result)


@router.post(
    "/{organization_id}/websites",
    status_code=HTTP_201_CREATED,
    response_model=WebsiteResponse,
    responses=ERROR_RESPONSES,
    name="website:create",
)
async def create_website(
    *,
    user: User = Depends(get_current_user_auth()),
    membership=Depends(
        require_org_role([OrganizationRoleEnum.admin, OrganizationRoleEnum.member])
    ),
    websites_service: WebsitesService = Depends(get_service(WebsitesService)),
    websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    organization_id: int,
    website_in: WebsiteInCreate,
):
    """Create a new website."""
    result = await websites_service.create_website(
        organization_id=organization_id,
        website_in=website_in,
        websites_repo=websites_repo,
    )
    return await handle_result(result)
