import pytest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from fastapi import HTTPException
from starlette import status

from app.models.organization import OrganizationMembership, OrganizationRoleEnum
from app.models.website import WebsiteMembership, WebsiteRoleEnum
from app.api.dependencies.role_checker import require_org_or_website_role
from app.core.constant import FAIL_INSUFFICIENT_PREVILEGES


@pytest.mark.asyncio
async def test_require_org_or_website_role_success_org_membership():
    """
    Scenario: organization_id is not provided.
    so, website_repo is queried to return a website with an associated organization.
    The user has a valid organization membership with an allowed role, `admin`.
    """
    # Arrange
    mocked_website = SimpleNamespace(organization_id=100)
    mocked_org_membership = OrganizationMembership(
        id=456,
        user_id=1,
        organization_id=100,
        role=OrganizationRoleEnum.admin,
        joined_at=datetime.now(timezone.utc),
    )
    allowed_org_roles = [OrganizationRoleEnum.admin]
    allowed_web_roles = [WebsiteRoleEnum.admin]
    dependency = require_org_or_website_role(allowed_org_roles, allowed_web_roles)

    mocked_signed_in_user = SimpleNamespace(id=1)

    org_memberships_repo = AsyncMock()
    org_memberships_repo.get_membership.return_value = mocked_org_membership

    web_memberships_repo = AsyncMock()
    web_memberships_repo.get_membership.return_value = None

    website_repo = AsyncMock()
    website_repo.get_website_by_id.return_value = mocked_website

    # Act
    result = await dependency(
        website_id=42,
        organization_id=None,
        token_user=mocked_signed_in_user,
        org_memberships_repo=org_memberships_repo,
        web_memberships_repo=web_memberships_repo,
        website_repo=website_repo,
    )

    # Assert: Should return the organization membership.
    assert result == mocked_org_membership


@pytest.mark.asyncio
async def test_require_org_or_website_role_success_web_membership():
    """
    Scenario: User doesn't belong to organisation,
    but the user belongs to the website with role `admin`.
    """
    # Arrange
    mocked_website = SimpleNamespace(organization_id=100)
    dummy_web_membership = WebsiteMembership(
        id=789,
        user_id=1,
        website_id=42,
        role=WebsiteRoleEnum.admin,
    )
    allowed_org_roles = [OrganizationRoleEnum.admin]
    allowed_web_roles = [WebsiteRoleEnum.admin]
    dependency = require_org_or_website_role(allowed_org_roles, allowed_web_roles)

    mocked_signed_in_user = SimpleNamespace(id=1)

    org_memberships_repo = AsyncMock()
    org_memberships_repo.get_membership.return_value = None

    web_memberships_repo = AsyncMock()
    web_memberships_repo.get_membership.return_value = dummy_web_membership

    website_repo = AsyncMock()
    website_repo.get_website_by_id.return_value = mocked_website

    # Act
    result = await dependency(
        website_id=42,
        organization_id=None,
        token_user=mocked_signed_in_user,
        org_memberships_repo=org_memberships_repo,
        web_memberships_repo=web_memberships_repo,
        website_repo=website_repo,
    )

    # Assert: Should return the website membership.
    assert result == dummy_web_membership


@pytest.mark.asyncio
async def test_require_org_or_website_role_failure_no_valid_membership():
    """
    Scenario: Neither a valid organization membership nor a valid website membership is found.
    """
    # Arrange
    dummy_website = SimpleNamespace(organization_id=100)
    allowed_org_roles = [OrganizationRoleEnum.admin]
    allowed_web_roles = [WebsiteRoleEnum.admin]
    dependency = require_org_or_website_role(allowed_org_roles, allowed_web_roles)

    dummy_signed_in_user = SimpleNamespace(id=1)

    org_memberships_repo = AsyncMock()
    org_memberships_repo.get_membership.return_value = None

    web_memberships_repo = AsyncMock()
    web_memberships_repo.get_membership.return_value = None

    website_repo = AsyncMock()
    website_repo.get_website_by_id.return_value = dummy_website

    # Act/Assert
    with pytest.raises(HTTPException) as exc_info:
        await dependency(
            website_id=42,
            organization_id=None,
            token_user=dummy_signed_in_user,
            org_memberships_repo=org_memberships_repo,
            web_memberships_repo=web_memberships_repo,
            website_repo=website_repo,
        )
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == FAIL_INSUFFICIENT_PREVILEGES


@pytest.mark.asyncio
async def test_require_org_or_website_role_failure_website_not_found():
    """
    Scenario: organization_id is not provided
    website_repo also fails to return valid membership record.
    """
    # Arrange
    allowed_org_roles = [OrganizationRoleEnum.admin]
    allowed_web_roles = [WebsiteRoleEnum.admin]
    dependency = require_org_or_website_role(allowed_org_roles, allowed_web_roles)

    mocked_signed_in_user = SimpleNamespace(id=1)

    org_memberships_repo = AsyncMock()
    org_memberships_repo.get_membership.return_value = None

    web_memberships_repo = AsyncMock()
    web_memberships_repo.get_membership.return_value = None

    website_repo = AsyncMock()
    website_repo.get_website_by_id.return_value = None

    # Act/Assert
    with pytest.raises(HTTPException) as exc_info:
        await dependency(
            website_id=42,
            organization_id=None,
            token_user=mocked_signed_in_user,
            org_memberships_repo=org_memberships_repo,
            web_memberships_repo=web_memberships_repo,
            website_repo=website_repo,
        )
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Website or associated organization not found"
