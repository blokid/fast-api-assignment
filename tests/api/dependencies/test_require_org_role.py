import pytest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from fastapi import HTTPException
from starlette import status
from app.models.organization import OrganizationMembership, OrganizationRoleEnum
from app.models.website import WebsiteMembership, WebsiteRoleEnum
from app.api.dependencies.role_checker import (
    require_org_role,
    require_org_or_website_role,
)
from app.core.constant import FAIL_INSUFFICIENT_PREVILEGES


@pytest.mark.asyncio
async def test_require_org_role_success():
    # Arrange
    dummy_org_membership = OrganizationMembership(
        id=456,
        user_id=1,
        organization_id=100,
        role=OrganizationRoleEnum.admin,
        joined_at=datetime.now(timezone.utc),
    )
    allowed_roles = [OrganizationRoleEnum.admin, OrganizationRoleEnum.member]
    dependency = require_org_role(allowed_roles)

    dummy_signed_in_user = SimpleNamespace(id=1)
    memberships_repo = AsyncMock()
    memberships_repo.get_membership.return_value = dummy_org_membership

    # Act
    result = await dependency(
        organization_id=100,
        token_user=dummy_signed_in_user,
        memberships_repo=memberships_repo,
    )

    # Assert
    assert result == dummy_org_membership


@pytest.mark.asyncio
async def test_require_org_role_failure_due_to_insufficient_role():
    # Arrange
    dummy_org_membership = OrganizationMembership(
        id=456,
        user_id=1,
        organization_id=100,
        role=OrganizationRoleEnum.member,  # Role not allowed in this test.
        joined_at=datetime.now(timezone.utc),
    )
    allowed_roles = [OrganizationRoleEnum.admin]
    dependency = require_org_role(allowed_roles)

    dummy_signed_in_user = SimpleNamespace(id=1)
    memberships_repo = AsyncMock()
    memberships_repo.get_membership.return_value = dummy_org_membership

    # Act/Assert
    with pytest.raises(HTTPException) as exc_info:
        await dependency(
            organization_id=100,
            token_user=dummy_signed_in_user,
            memberships_repo=memberships_repo,
        )
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == FAIL_INSUFFICIENT_PREVILEGES
