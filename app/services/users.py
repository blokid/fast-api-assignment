import logging

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from app.services.email import EmailService
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from app.api.dependencies.database import get_repository
from app.api.dependencies.users import get_users_filters
from app.core import constant, token
from app.database.repositories.users import UsersRepository
from app.database.repositories.organizations import OrganizationsRepository
from app.database.repositories.organization_memberships import (
    OrganizationMembershipsRepository,
)

from app.models.user import User
from app.schemas.user import (
    UserAuthOutData,
    UserInCreate,
    UserInSignIn,
    UserInUpdate,
    UserOutData,
    UserResponse,
    UsersFilters,
    SignupResponse,
)
from app.schemas.organization_membership import OrganizationMembershipInCreate
from app.schemas.organization import OrganizationInCreate
from app.services.base import BaseService
from app.utils import ServiceResult, response_4xx, response_5xx, return_service
from app.api.dependencies.service import get_service

logger = logging.getLogger(__name__)


class UsersService(BaseService):
    @return_service
    async def get_user_by_id(
        self,
        user_id: int,
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    ) -> ServiceResult:
        user = await users_repo.get_user_by_id(user_id=user_id)
        if not user:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_VALIDATION_MATCHED_USER_ID},
            )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_MATCHED_USER_ID,
                "data": jsonable_encoder(UserOutData.model_validate(user)),
            },
        )

    @return_service
    async def get_user_by_token(
        self,
        token_user: User,
    ) -> ServiceResult:
        if not token_user:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": constant.FAIL_VALIDATION_MATCHED_USER_TOKEN},
            )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_MATCHED_USER_TOKEN,
                "data": jsonable_encoder(UserOutData.model_validate(token_user)),
            },
        )

    @return_service
    async def get_users(
        self,
        users_filters: UsersFilters = Depends(get_users_filters),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    ) -> UserResponse:
        users = await users_repo.get_filtered_users(
            skip=users_filters.skip, limit=users_filters.limit
        )

        if not users:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_VALIDATION_MATCHED_FILTERED_USERS},
            )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_GET_USERS,
                "data": jsonable_encoder(
                    [UserOutData.model_validate(user) for user in users]
                ),
            },
        )

    @return_service
    async def signup_user(
        self,
        user_in: UserInCreate,
        users_repo: UsersRepository,
        email_service: EmailService,
        organizations_repo: OrganizationsRepository,
        organization_memberships_repo: OrganizationMembershipsRepository,
        secret_key: str = "",
    ) -> SignupResponse:
        try:
            duplicate_user = await users_repo.get_duplicated_user(user_in=user_in)
            if duplicate_user:
                return response_4xx(
                    status_code=HTTP_400_BAD_REQUEST,
                    context={"reason": constant.FAIL_VALIDATION_USER_DUPLICATED},
                )

            # TODO: Begin DB Transaction

            email_verification_token = token.create_email_verification_token(
                email=user_in.email, secret_key=secret_key
            )

            created_user = await users_repo.signup_user(
                user_in=user_in, email_verification_token=email_verification_token
            )

            created_organization = await organizations_repo.create_organization(
                organization_in=OrganizationInCreate(
                    name=created_user.username + constant.DEFAULT_ORG_NAME_POSTFIX,
                    description="",
                )
            )

            await organization_memberships_repo.add_member(
                organization_id=created_organization.id,
                user_id=created_user.id,
                role="admin",
            )

            # TODO: Commit DB Transaction
            email_service.send_verification_email(
                email=created_user.email,
                verification_token=email_verification_token,
                username=created_user.username,
            )
            return dict(
                status_code=HTTP_201_CREATED,
                content={
                    "message": constant.SUCCESS_SIGN_UP,
                },
            )
        except Exception as e:
            # TODO: Rollback DB Transaction
            return response_5xx(
                context={"reason": f"An error occurred during signup: {str(e)}"},
            )

    @return_service
    async def signin_user(
        self,
        user_in: UserInSignIn,
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        secret_key: str = "",
    ) -> UserResponse:
        searched_user = await users_repo.get_user_by_email(email=user_in.email)

        if not searched_user:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": constant.FAIL_VALIDATION_MATCHED_USER_EMAIL},
            )

        if not searched_user.email_verified:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": constant.FAIL_VALIDATION_USER_NOT_VERIFIED},
            )

        validation_password = await users_repo.get_user_password_validation(
            user=searched_user, password=user_in.password
        )
        if not validation_password:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": constant.FAIL_VALIDATION_USER_WRONG_PASSWORD},
            )

        if searched_user.deleted_at:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": constant.FAIL_VALIDATION_USER_DELETED},
            )

        created_token = token.create_token_for_user(
            user=searched_user, secret_key=secret_key
        )
        user_data_with_auth = UserAuthOutData.model_validate(searched_user)

        user_data_with_auth.token = created_token

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_SIGN_IN,
                "data": jsonable_encoder(user_data_with_auth),
            },
        )

    @return_service
    async def update_user(
        self,
        token_user: User,
        user_in: UserInUpdate,
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    ) -> UserResponse:
        updated_user = await users_repo.update_user(user=token_user, user_in=user_in)

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_UPDATE_USER,
                "data": jsonable_encoder(UserOutData.model_validate(updated_user)),
            },
        )

    @return_service
    async def delete_user(
        self,
        token_user: User,
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    ) -> ServiceResult:
        deleted_user = await users_repo.delete_user(user=token_user)

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_DELETE_USER,
                "data": jsonable_encoder(deleted_user),
            },
        )

    @return_service
    async def verify_user(
        self,
        verification_token: str,
        users_repo: UsersRepository,
        secret_key: str = "",
    ) -> ServiceResult:
        try:
            email = token.verify_email_verification_token(
                token=verification_token,
                secret_key=secret_key,
            )
        except ValueError as e:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": str(e)},
            )

        user = await users_repo.get_user_by_email(email=email)
        if not user:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_USER_NOT_FOUND},
            )

        if user.email_verified:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": constant.FAIL_ALREADY_VERIFIED},
            )

        await users_repo.update_user_verification_status(
            user_id=user.id, email_verified=True
        )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_VERIFICATION_COMPLETED,
            },
        )
