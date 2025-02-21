import pytest
from unittest.mock import AsyncMock, MagicMock
from app.schemas.user import UserInSignIn
from app.services.users import UsersService
from app.core import constant
from app.utils import AppExceptionCase
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from app.core.token import UserTokenData


from types import SimpleNamespace


@pytest.mark.asyncio
async def test_signin_user_positive():
    # Arrange
    user_in = UserInSignIn(email="testuser@example.com", password="password123")

    created_token = UserTokenData(
        access_token="mocked_access_token", token_type="bearer"
    )

    dummy_user = SimpleNamespace(
        id=1,
        username="testuser",
        email=user_in.email,
        email_verified=True,
        deleted_at=None,
    )
    dummy_user.token = created_token
    users_repo = AsyncMock()
    users_repo.get_user_by_email.return_value = dummy_user
    users_repo.get_user_password_validation.return_value = True

    # Act
    service = UsersService()
    result = await service.signin_user(
        user_in=user_in,
        users_repo=users_repo,
        secret_key="test_secret",
    )

    # Assert
    response_data = result.json()
    assert result.result.status_code == HTTP_200_OK
    assert response_data["message"] == constant.SUCCESS_SIGN_IN
    token_data = response_data["data"]["token"]
    assert isinstance(token_data, dict)
    assert "access_token" in token_data
    assert "token_type" in token_data
    assert token_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_signin_user_email_not_verified():
    """Test signin fails when the user's email is not verified."""
    # Arrange
    user_in = UserInSignIn(email="testuser@example.com", password="password123")
    dummy_user = SimpleNamespace(
        id=1,
        username="testuser",
        email=user_in.email,
        email_verified=False,  # Email not verified
        deleted_at=None,
    )
    users_repo = AsyncMock()
    users_repo.get_user_by_email.return_value = dummy_user

    # Act
    service = UsersService()
    result = await service.signin_user(
        user_in=user_in,
        users_repo=users_repo,
        secret_key="test_secret",
    )

    # Assert
    assert result.result.status_code == HTTP_400_BAD_REQUEST
    assert result.result.context["reason"] == constant.FAIL_VALIDATION_USER_NOT_VERIFIED
    users_repo.get_user_by_email.assert_called_once_with(email=user_in.email)


@pytest.mark.asyncio
async def test_signin_user_wrong_password():
    """Test signin fails when password validation fails."""
    # Arrange
    user_in = UserInSignIn(email="testuser@example.com", password="wrongpassword")
    dummy_user = SimpleNamespace(
        id=1,
        username="testuser",
        email=user_in.email,
        email_verified=True,
        deleted_at=None,
    )
    users_repo = AsyncMock()
    users_repo.get_user_by_email.return_value = dummy_user
    users_repo.get_user_password_validation.return_value = False  # Wrong password

    # Act
    service = UsersService()
    result = await service.signin_user(
        user_in=user_in,
        users_repo=users_repo,
        secret_key="test_secret",
    )

    # Assert
    assert result.result.status_code == HTTP_400_BAD_REQUEST
    assert (
        result.result.context["reason"] == constant.FAIL_VALIDATION_USER_WRONG_PASSWORD
    )
    users_repo.get_user_by_email.assert_called_once_with(email=user_in.email)
    users_repo.get_user_password_validation.assert_called_once_with(
        user=dummy_user, password=user_in.password
    )


@pytest.mark.asyncio
async def test_signin_user_user_deleted():
    """Test signin fails when the user account is marked as deleted."""
    # Arrange
    user_in = UserInSignIn(email="testuser@example.com", password="password123")
    dummy_user = SimpleNamespace(
        id=1,
        username="testuser",
        email=user_in.email,
        email_verified=True,
        deleted_at="2025-01-01",
    )
    users_repo = AsyncMock()
    users_repo.get_user_by_email.return_value = dummy_user
    users_repo.get_user_password_validation.return_value = True  # Password is valid

    # Act
    service = UsersService()
    result = await service.signin_user(
        user_in=user_in,
        users_repo=users_repo,
        secret_key="test_secret",
    )

    # Assert
    assert result.result.status_code == HTTP_400_BAD_REQUEST
    assert result.result.context["reason"] == constant.FAIL_VALIDATION_USER_DELETED
    users_repo.get_user_by_email.assert_called_once_with(email=user_in.email)
    users_repo.get_user_password_validation.assert_called_once_with(
        user=dummy_user, password=user_in.password
    )
