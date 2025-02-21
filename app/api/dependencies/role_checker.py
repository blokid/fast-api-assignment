from fastapi import Depends, HTTPException, status
from typing import List, Optional
from app.models.user import User
from app.api.dependencies.auth import get_current_user_auth
from app.database.repositories.organization_memberships import (
    OrganizationMembershipsRepository,
)
from app.database.repositories.website_memberships import WebsiteMembershipsRepository
from app.api.dependencies.database import get_repository
from app.models.organization import OrganizationRoleEnum
from app.models.website import WebsiteRoleEnum
from app.core.constant import FAIL_INSUFFICIENT_PREVILEGES
from app.models.website import WebsiteRoleEnum
from app.database.repositories.websites import WebsitesRepository


def require_website_role(allowed_roles: List[WebsiteRoleEnum]):
    async def website_role_dependency(
        website_id: int,
        token_user: User = Depends(get_current_user_auth()),
        memberships_repo: WebsiteMembershipsRepository = Depends(
            get_repository(WebsiteMembershipsRepository)
        ),
    ):
        membership = await memberships_repo.get_membership(
            user_id=token_user.id, website_id=website_id
        )
        if membership and membership.role in allowed_roles:
            return membership
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=FAIL_INSUFFICIENT_PREVILEGES,
        )

    return website_role_dependency


def require_org_role(allowed_roles: List[OrganizationRoleEnum]):
    async def org_role_dependency(
        organization_id: int,
        token_user: User = Depends(get_current_user_auth()),
        memberships_repo: OrganizationMembershipsRepository = Depends(
            get_repository(OrganizationMembershipsRepository)
        ),
    ):
        membership = await memberships_repo.get_membership(
            user_id=token_user.id, organization_id=organization_id
        )
        if membership and membership.role in allowed_roles:
            return membership
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=FAIL_INSUFFICIENT_PREVILEGES,
        )

    return org_role_dependency


def require_org_or_website_role(
    org_roles: Optional[List[OrganizationRoleEnum]] = None,
    web_roles: Optional[List[WebsiteRoleEnum]] = None,
):
    async def dependency(
        website_id: int,
        organization_id: Optional[int] = None,
        token_user: User = Depends(get_current_user_auth()),
        org_memberships_repo: OrganizationMembershipsRepository = Depends(
            get_repository(OrganizationMembershipsRepository)
        ),
        web_memberships_repo: WebsiteMembershipsRepository = Depends(
            get_repository(WebsiteMembershipsRepository)
        ),
        website_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    ):
        if organization_id is None:
            website = await website_repo.get_website_by_id(website_id=website_id)
            if website is None or website.organization_id is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Website or associated organization not found",
                )
            organization_id = website.organization_id

        if org_roles:
            org_membership = await org_memberships_repo.get_membership(
                user_id=token_user.id, organization_id=organization_id
            )
            if org_membership and org_membership.role in org_roles:
                return org_membership

        if web_roles:
            web_membership = await web_memberships_repo.get_membership(
                user_id=token_user.id, website_id=website_id
            )
            if web_membership and web_membership.role in web_roles:
                return web_membership

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=FAIL_INSUFFICIENT_PREVILEGES,
        )

    return dependency
