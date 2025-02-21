import pytest
from unittest.mock import AsyncMock, MagicMock
from app.schemas.user import UserInCreate
from app.services.users import UsersService
from app.core import constant
from app.utils import AppExceptionCase
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


@pytest.mark.asyncio
async def test_signup_user_positive():
    """Test positive scenario for signup_user."""

    # Arrange
    user_in = UserInCreate(
        username="testuser", email="testuser@example.com", password="password123"
    )
    users_repo = AsyncMock()
    users_repo.get_duplicated_user.return_value = None  # No duplicate user
    users_repo.signup_user.return_value = MagicMock(
        id=1, username="testuser", email="testuser@example.com"
    )

    organizations_repo = AsyncMock()
    organizations_repo.create_organization.return_value = MagicMock(id=1)

    organization_memberships_repo = AsyncMock()
    email_service = MagicMock()

    # Act
    service = UsersService()
    result = await service.signup_user(
        user_in=user_in,
        users_repo=users_repo,
        email_service=email_service,
        organizations_repo=organizations_repo,
        organization_memberships_repo=organization_memberships_repo,
        secret_key="test_secret",
    )

    # Assert
    assert result.json()["message"] == constant.SUCCESS_SIGN_UP
    users_repo.get_duplicated_user.assert_called_once_with(user_in=user_in)
    users_repo.signup_user.assert_called_once()
    organizations_repo.create_organization.assert_called_once()
    organization_memberships_repo.add_member.assert_called_once()
    email_service.send_verification_email.assert_called_once()


@pytest.mark.asyncio
async def test_signup_user_duplicate_user():
    """Test signup fails due to duplicate user."""

    # Arrange
    user_in = UserInCreate(
        username="existinguser", email="existing@example.com", password="password123"
    )
    users_repo = AsyncMock()
    users_repo.get_duplicated_user.return_value = True

    # Act
    service = UsersService()
    result = await service.signup_user(
        user_in=user_in,
        users_repo=users_repo,
        email_service=MagicMock(),
        organizations_repo=AsyncMock(),
        organization_memberships_repo=AsyncMock(),
        secret_key="test_secret",
    )

    # Assert
    assert result.result.status_code == HTTP_400_BAD_REQUEST
    assert result.result.context["reason"] == constant.FAIL_VALIDATION_USER_DUPLICATED
    users_repo.get_duplicated_user.assert_called_once_with(user_in=user_in)


@pytest.mark.asyncio
async def test_signup_user_database_error():
    """Test signup fails due to user database error."""

    # Arrange
    USER_DB_FAILURE_ERROR_MSG = "Unknown error in user db"
    user_in = UserInCreate(
        username="testuser", email="testuser@example.com", password="password123"
    )
    users_repo = AsyncMock()
    users_repo.get_duplicated_user.return_value = None
    users_repo.signup_user.side_effect = AppExceptionCase(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        context={USER_DB_FAILURE_ERROR_MSG},
    )

    # Act
    service = UsersService()
    result = await service.signup_user(
        user_in=user_in,
        users_repo=users_repo,
        email_service=MagicMock(),
        organizations_repo=AsyncMock(),
        organization_memberships_repo=AsyncMock(),
        secret_key="test_secret",
    )

    # Assert
    assert result.result.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert USER_DB_FAILURE_ERROR_MSG in result.result.context["reason"]
    users_repo.signup_user.assert_called_once()
    # TODO: test if the db session is rollback
