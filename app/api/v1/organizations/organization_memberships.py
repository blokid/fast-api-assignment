from fastapi import APIRouter, Depends, status, Path
from app.api.dependencies.auth import get_current_user_auth
from app.api.dependencies.role_checker import require_org_role
from app.models.user import User
from app.api.dependencies.database import get_repository
from app.models.organization import OrganizationRoleEnum
from app.schemas.organization_membership import (
    OrganizationMembershipInCreate,
    OrganizationMembershipResponse,
)
from app.services.organization_memberships import OrganizationMembershipsService
from app.api.dependencies.service import get_service
from app.utils import handle_result
from app.database.repositories.organization_memberships import (
    OrganizationMembershipsRepository,
)

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=OrganizationMembershipResponse,
    summary="Add a new member to an organization",
)
async def add_organization_membership(
    membership_in: OrganizationMembershipInCreate,
    membership=Depends(require_org_role([OrganizationRoleEnum.admin])),
    token_user: User = Depends(get_current_user_auth),
    organization_memberships_service: OrganizationMembershipsService = Depends(
        get_service(OrganizationMembershipsService)
    ),
    organization_memberships_repo: OrganizationMembershipsRepository = Depends(
        get_repository(OrganizationMembershipsRepository)
    ),
    organization_id: int = Path(..., description="The organization ID"),
):
    result = await organization_memberships_service.add_member(
        organization_id=organization_id,
        membership_in=membership_in,
        organization_memberships_repo=organization_memberships_repo,
    )
    return await handle_result(result)


@router.delete(
    "/{membership_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove a member from an organization",
)
async def remove_organization_membership(
    membership_id: int = Path(..., description="The membership ID"),
    membership=Depends(require_org_role([OrganizationRoleEnum.admin])),
    token_user: User = Depends(get_current_user_auth()),
    organization_memberships_repo: OrganizationMembershipsRepository = Depends(
        get_repository(OrganizationMembershipsRepository)
    ),
    organization_memberships_service: OrganizationMembershipsService = Depends(
        get_service(OrganizationMembershipsService)
    ),
):
    result = await organization_memberships_service.remove_member(
        membership_id=membership_id,
        organization_memberships_repo=organization_memberships_repo,
    )
    return await handle_result(result)
