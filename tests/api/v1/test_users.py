from os import environ

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

# from fastapi.testclient import TestClient
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.core import constant, settings, token
from app.schemas.token import TokenInvite
from app.schemas.user import UserBase, VerificationTokenData

environ["APP_ENV"] = "test"

pytestmark = pytest.mark.asyncio


async def test_signup(
    app: FastAPI,
    client: AsyncClient,
    random_user: dict[str, str],
    created_random_user: dict[str, str],
) -> None:
    response = await client.post(app.url_path_for("auth:signup"), json=random_user)
    result = response.json()
    assert result.get("message") == constant.SUCCESS_VERIFICATION_EMAIL
    assert result.get("data") == {}
    assert response.status_code == HTTP_201_CREATED


async def test_signup_duplicate_user(
    app: FastAPI, client: AsyncClient, random_user: dict[str, str]
) -> None:
    response = await client.post(app.url_path_for("auth:signup"), json=random_user)
    result = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert result.get("app_exception") == "Response4XX"
    assert result["context"].get("reason") == constant.FAIL_VALIDATION_USER_DUPLICATED


async def test_verification_email(
    app: FastAPI, client: AsyncClient, created_random_user: dict[str, str]
) -> None:
    verification_token: VerificationTokenData = token.create_verification_token(
        user=UserBase(**created_random_user),
        secret_key=settings.secret_key.get_secret_value(),
    )
    response = await client.post(
        app.url_path_for("auth:verify"), json={"token": verification_token.token}
    )
    result = response.json()
    created_random_user["id"] = result.get("data").get("id")
    assert response.status_code == HTTP_200_OK
    assert result["message"] == constant.SUCCESS_VERIFY_USER


async def test_signin_error(
    app: FastAPI,
    client: AsyncClient,
    created_random_user: dict[str, str],
    invalid_user: dict[str, str],
) -> None:
    # FAIL_VALIDATION_MATCHED_USER_EMAIL
    response = await client.post(app.url_path_for("auth:signin"), json=invalid_user)
    result = response.json()

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert result.get("app_exception") == "Response4XX"
    assert (
        result["context"].get("reason") == constant.FAIL_VALIDATION_MATCHED_USER_EMAIL
    )

    # FAIL_VALIDATION_USER_WRONG_PASSWORD
    invalid_user["email"] = created_random_user["email"]
    response = await client.post(app.url_path_for("auth:signin"), json=invalid_user)
    result = response.json()

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert result.get("app_exception") == "Response4XX"
    assert (
        result["context"].get("reason") == constant.FAIL_VALIDATION_USER_WRONG_PASSWORD
    )


async def test_signin(
    app: FastAPI, client: AsyncClient, created_random_user: dict[str, str]
) -> None:
    response = await client.post(
        app.url_path_for("auth:signin"), json=created_random_user
    )
    result = response.json()
    token = result.get("data").get("token")

    assert response.status_code == HTTP_200_OK
    assert result.get("message") == constant.SUCCESS_SIGN_IN
    assert token.get("access_token")
    assert token.get("token_type") == settings.jwt_token_prefix

    created_random_user["token"] = token


async def test_auth_info(
    app: FastAPI, client: AsyncClient, created_random_user: dict[str, str]
) -> None:
    headers = {
        "Authorization": f"{settings.jwt_token_prefix} {created_random_user.get('token').get('access_token')}",
        **client.headers,
    }
    response = await client.get(app.url_path_for("auth:info"), headers=headers)
    result = response.json()

    result_user = result.get("data")

    assert response.status_code == HTTP_200_OK
    assert result.get("message") == constant.SUCCESS_MATCHED_USER_TOKEN
    assert result_user.get("id") == created_random_user.get("id")
    assert result_user.get("username") == created_random_user.get("username")
    assert result_user.get("email") == created_random_user.get("email")


async def test_auto_created_org(
    app: FastAPI, client: AsyncClient, created_random_user: dict[str, str]
) -> None:
    headers = {
        "Authorization": f"{settings.jwt_token_prefix} {created_random_user.get('token').get('access_token')}",
        **client.headers,
    }
    response = await client.get(
        app.url_path_for("user:organizations"),
        headers=headers,
    )
    result = response.json()
    assert result["message"] == constant.SUCCESS_GET_USER_ORGANIZATION
    assert len(result["data"]["organizations"]) == 1
    assert response.status_code == HTTP_200_OK


async def test_all_user(app: FastAPI, client: AsyncClient) -> None:
    response = await client.get(app.url_path_for("users:all"))

    result = response.json()
    assert response.status_code == HTTP_200_OK
    assert result.get("message") == constant.SUCCESS_GET_USERS
    assert isinstance(result.get("data"), list)


async def test_user_by_id(
    app: FastAPI, client: AsyncClient, created_random_user: dict[str, str]
) -> None:
    headers = {
        "Authorization": f"{settings.jwt_token_prefix} {created_random_user.get('token').get('access_token')}",
        **client.headers,
    }
    response = await client.get(
        app.url_path_for("user:info-by-id", user_id=created_random_user.get("id")),
        headers=headers,
    )

    result = response.json()
    assert response.status_code == HTTP_200_OK
    assert result.get("message") == constant.SUCCESS_MATCHED_USER_ID
    assert result.get("data").get("id") == created_random_user.get("id")
    assert result.get("data").get("username") == created_random_user.get("username")
    assert result.get("data").get("email") == created_random_user.get("email")


async def test_user_by_id_error(
    app: FastAPI, client: AsyncClient, created_random_user: dict[str, str]
) -> None:
    headers = {
        "Authorization": f"{settings.jwt_token_prefix} {created_random_user.get('token').get('access_token')}",
        **client.headers,
    }
    response = await client.get(
        app.url_path_for("user:info-by-id", user_id=-1),
        headers=headers,
    )

    result = response.json()
    assert response.status_code == HTTP_404_NOT_FOUND
    assert result.get("app_exception") == "Response4XX"
    assert result["context"].get("reason") == constant.FAIL_VALIDATION_MATCHED_USER_ID


async def test_update_user(
    app: FastAPI, client: AsyncClient, created_random_user: dict[str, str]
) -> None:
    headers = {
        "Authorization": f"{settings.jwt_token_prefix} {created_random_user.get('token').get('access_token')}",
        **client.headers,
    }

    update_user = {
        "username": "new_username",
        **created_random_user,
    }
    response = await client.patch(
        app.url_path_for("user:patch-by-id"),
        json=update_user,
        headers=headers,
    )

    result = response.json()
    assert response.status_code == HTTP_200_OK
    assert result.get("message") == constant.SUCCESS_UPDATE_USER
    assert result.get("data").get("id") == update_user.get("id")
    assert result.get("data").get("username") == update_user.get("username")
    assert result.get("data").get("email") == update_user.get("email")


async def test_create_organization(
    app: FastAPI,
    client: AsyncClient,
    created_random_user: dict[str, str],
    random_org: dict[str, str],
    created_random_org: dict[str, str],
) -> None:
    headers = {
        "Authorization": f"{settings.jwt_token_prefix} {created_random_user.get('token').get('access_token')}",
        **client.headers,
    }
    response = await client.post(
        app.url_path_for("organization:create"),
        json=random_org,
        headers=headers,
    )
    result = response.json()
    assert response.status_code == HTTP_201_CREATED
    assert result.get("message") == constant.SUCCESS_CREATE_ORGANIZATION
    assert result.get("data").get("name") == random_org.get("name")
    created_random_org.update(result.get("data"))


async def test_update_organization(
    app: FastAPI,
    client: AsyncClient,
    created_random_user: dict[str, str],
    random_org: dict[str, str],
    created_random_org: dict[str, str],
) -> None:
    headers = {
        "Authorization": f"{settings.jwt_token_prefix} {created_random_user.get('token').get('access_token')}",
        **client.headers,
    }
    random_org["name"] = "new org name"
    response = await client.patch(
        app.url_path_for(
            "organization:update", organization_id=created_random_org["id"]
        ),
        json=random_org,
        headers=headers,
    )
    result = response.json()
    assert response.status_code == HTTP_200_OK
    assert result.get("message") == constant.SUCCESS_UPDATE_ORGANIZATION
    assert result.get("data").get("name") == random_org.get("name")
    created_random_org.update(result.get("data"))


async def test_organization_invite(
    app: FastAPI,
    client: AsyncClient,
    created_random_user: dict[str, str],
    random_invite: dict[str, str],
    created_random_org: dict[str, str],
) -> None:
    headers = {
        "Authorization": f"{settings.jwt_token_prefix} {created_random_user.get('token').get('access_token')}",
        **client.headers,
    }
    response = await client.post(
        app.url_path_for(
            "organization:invite", organization_id=created_random_org["id"]
        ),
        json=random_invite,
        headers=headers,
    )
    result = response.json()
    assert response.status_code == HTTP_200_OK
    assert result.get("message") == constant.SUCCESS_INVITATION_EMAIL
    created_random_org.update(result.get("data"))


async def test_accept_organization_invitation(
    app: FastAPI,
    client: AsyncClient,
    random_invite: dict[str, str],
    created_random_org: dict[str, str],
) -> None:
    created_token = token.create_org_invitation_token(
        invite=TokenInvite(
            organization_id=created_random_org["id"], email=random_invite["email"]
        ),
        secret_key=settings.secret_key.get_secret_value(),
    )
    response = await client.post(
        app.url_path_for("organization:accept-invite"),
        json={"token": created_token.token},
    )
    result = response.json()
    assert response.status_code == HTTP_404_NOT_FOUND
    assert result.get("context").get("reason") == constant.FAIL_NEED_TO_SIGN_UP


async def test_delete_organization(
    app: FastAPI,
    client: AsyncClient,
    created_random_user: dict[str, str],
    created_random_org: dict[str, str],
) -> None:
    headers = {
        "Authorization": f"{settings.jwt_token_prefix} {created_random_user.get('token').get('access_token')}",
        **client.headers,
    }
    response = await client.delete(
        app.url_path_for(
            "organization:update", organization_id=created_random_org["id"]
        ),
        headers=headers,
    )
    result = response.json()
    assert response.status_code == HTTP_200_OK
    assert result.get("message") == constant.SUCCESS_DELETE_ORGANIZATION
    assert result.get("data").get("deleted_at") is not None
    created_random_org.update(result.get("data"))


async def test_delete_user(
    app: FastAPI, client: AsyncClient, created_random_user: dict[str, str]
) -> None:
    headers = {
        "Authorization": f"{settings.jwt_token_prefix} {created_random_user.get('token').get('access_token')}",
        **client.headers,
    }
    response = await client.delete(
        app.url_path_for("user:delete-by-id"), headers=headers
    )

    result = response.json()
    assert response.status_code == HTTP_200_OK
    assert result.get("message") == constant.SUCCESS_DELETE_USER
