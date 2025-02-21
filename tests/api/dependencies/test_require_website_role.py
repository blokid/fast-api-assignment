import pytest
from unittest.mock import AsyncMock
from types import SimpleNamespace
from fastapi import HTTPException
from starlette import status
from app.models.website import WebsiteMembership
from app.api.dependencies.auth import get_current_user_auth
from app.api.dependencies.role_checker import require_website_role
from app.models.website import WebsiteRoleEnum
from app.core.constant import FAIL_INSUFFICIENT_PREVILEGES
from datetime import datetime


@pytest.mark.asyncio
async def test_require_website_role_success():
    # Arrange
    mocked_membereship_record = WebsiteMembership(
        id=123,
        user_id=1,
        website_id=42,
        role=WebsiteRoleEnum.admin,
    )
    allowed_roles = [WebsiteRoleEnum.admin, WebsiteRoleEnum.member]
    dependency = require_website_role(allowed_roles)

    mocked_signin_user = SimpleNamespace(id=1)
    memberships_repo = AsyncMock()
    memberships_repo.get_membership.return_value = mocked_membereship_record

    # Act
    result = await dependency(
        website_id=42,
        token_user=mocked_signin_user,
        memberships_repo=memberships_repo,
    )

    # Assert
    assert result == mocked_membereship_record


@pytest.mark.asyncio
async def test_require_website_role_failure_due_to_insufficient_role():
    # Arrange
    mocked_membership_record = WebsiteMembership(
        id=123,
        user_id=1,
        website_id=42,
        role=WebsiteRoleEnum.member,
    )
    allowed_roles = [WebsiteRoleEnum.admin]
    dependency = require_website_role(allowed_roles)

    mocked_signed_in_user = SimpleNamespace(id=1)
    memberships_repo = AsyncMock()
    memberships_repo.get_membership.return_value = mocked_membership_record

    # Act/Assert
    with pytest.raises(HTTPException) as exc_info:
        await dependency(
            website_id=42,
            token_user=mocked_signed_in_user,
            memberships_repo=memberships_repo,
        )
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Insufficient privileges"
