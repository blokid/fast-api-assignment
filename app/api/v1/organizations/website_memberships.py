# website_membership_routes.py (Website Membership Routes)

from fastapi import APIRouter, Depends, status, Path
from app.api.dependencies.auth import get_current_user_auth
from app.api.dependencies.role_checker import (
    require_website_role,
    require_org_or_website_role,
)
from app.models.user import User
from app.api.dependencies.database import get_repository
from app.models.website import WebsiteRoleEnum
from app.models.organization import OrganizationRoleEnum
from app.schemas.website_membership import (
    WebsiteMembershipInCreate,
    WebsiteMembershipResponse,
)
from app.services.website_memberships import WebsiteMembershipsService
from app.api.dependencies.service import get_service
from app.utils import handle_result
from app.database.repositories.website_memberships import (
    WebsiteMembershipsRepository,
)
from app.database.repositories.websites import WebsitesRepository

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=WebsiteMembershipResponse,
    summary="Add a new member to a website",
)
async def add_website_membership(
    membership_in: WebsiteMembershipInCreate,
    membership=Depends(
        require_org_or_website_role(
            [OrganizationRoleEnum.admin], [WebsiteRoleEnum.admin]
        )
    ),
    token_user: User = Depends(get_current_user_auth),
    website_memberships_service: WebsiteMembershipsService = Depends(
        get_service(WebsiteMembershipsService)
    ),
    website_memberships_repo: WebsiteMembershipsRepository = Depends(
        get_repository(WebsiteMembershipsRepository)
    ),
    website_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    website_id: int = Path(..., description="The website ID"),
):
    """Add a new member to a website."""
    result = await website_memberships_service.add_member(
        website_id=website_id,
        membership_in=membership_in,
        website_memberships_repo=website_memberships_repo,
    )
    return await handle_result(result)


@router.delete(
    "/{membership_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove a member from a website",
)
async def remove_website_membership(
    membership_id: int = Path(..., description="The membership ID"),
    membership=Depends(
        require_org_or_website_role(
            [OrganizationRoleEnum.admin], [WebsiteRoleEnum.admin]
        )
    ),
    token_user: User = Depends(get_current_user_auth()),
    website_memberships_repo: WebsiteMembershipsRepository = Depends(
        get_repository(WebsiteMembershipsRepository)
    ),
    website_memberships_service: WebsiteMembershipsService = Depends(
        get_service(WebsiteMembershipsService)
    ),
):
    """Remove a website membership by membership_id."""
    result = await website_memberships_service.remove_member(
        membership_id=membership_id,
        website_memberships_repo=website_memberships_repo,
    )
    return await handle_result(result)
