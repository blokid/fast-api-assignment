import logging

from fastapi import BackgroundTasks, Depends
from fastapi.encoders import jsonable_encoder
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from app.api.dependencies.database import get_repository
from app.core import constant, token
from app.database.repositories.organizations import OrganizationsRepository
from app.database.repositories.users import UsersRepository
from app.database.repositories.websites import WebsitesRepository
from app.models import User, Website, WebsiteInvite
from app.models.organization import Organization
from app.schemas.user import UserOutData
from app.schemas.website import (
    WebsiteInCreate,
    WebsiteInviteIn,
    WebsiteOutData,
    WebsiteResponse,
)
from app.schemas.website_user import (
    WebsiteUser,
    WebsiteUserOutData,
    WebsiteUserResponse,
)
from app.services.base import BaseService
from app.utils import (
    email,
    response_4xx,
    return_service,
)

logger = logging.getLogger(__name__)


class WebsitesService(BaseService):

    @return_service
    async def create_website(
        self,
        organization_id: int,
        website_in: WebsiteInCreate,
        user: User,
        websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
        orgs_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> WebsiteResponse:
        duplicate_website = await websites_repo.get_duplicate_website(
            website_in=website_in
        )
        if duplicate_website:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": constant.FAIL_VALIDATION_ORGANIZATION_DUPLICATED},
            )
        organization: Organization = await orgs_repo.get_organization_by_id(
            organization_id=organization_id
        )
        if not organization:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NO_ORGANIZATION},
            )
        if not user.is_member_of(organization_id=organization_id):
            return response_4xx(
                status_code=HTTP_403_FORBIDDEN,
                context={"reason": constant.FAIL_NOT_ALLOWED},
            )
        created_website = await websites_repo.create_website(
            website_in=website_in, user=user, organization=organization
        )

        return dict(
            status_code=HTTP_201_CREATED,
            content={
                "message": constant.SUCCESS_CREATE_ORGANIZATION,
                "data": jsonable_encoder(
                    WebsiteOutData.model_validate(created_website)
                ),
            },
        )

    @return_service
    async def get_websites(
        self,
        websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    ) -> WebsiteResponse:
        websites = await websites_repo.get_websites()

        if not websites:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NO_ORGANIZATION},
            )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_GET_ORGANIZATION,
                "data": jsonable_encoder(
                    [WebsiteOutData.model_validate(org) for org in websites]
                ),
            },
        )

    @return_service
    async def get_website(
        self,
        user: User,
        website_id: int,
        orgs_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    ) -> WebsiteResponse:
        website = await orgs_repo.get_website_by_id(website_id=website_id)

        if not website:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NO_ORGANIZATION},
            )
        if not await user.is_member_of(website.id):
            return response_4xx(
                status_code=HTTP_403_FORBIDDEN,
                context={"reason": constant.FAIL_NOT_ALLOWED},
            )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_GET_ORGANIZATION,
                "data": jsonable_encoder(WebsiteOutData.model_validate(website)),
            },
        )

    @return_service
    async def delete_website(
        self,
        user: User,
        website_id: int,
        orgs_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    ) -> WebsiteResponse:
        website = await orgs_repo.get_website_by_id(website_id=website_id)

        if not website:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NO_ORGANIZATION},
            )
        if not await user.is_admin_of(website.id):
            return response_4xx(
                status_code=HTTP_403_FORBIDDEN,
                context={"reason": constant.FAIL_NOT_ALLOWED},
            )

        await orgs_repo.delete_website(website_id=website_id)

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_DELETE_ORGANIZATION,
            },
        )

    @return_service
    async def invite_to_website(
        self,
        user: User,
        website_id: int,
        background_tasks: BackgroundTasks,
        secret_key: str,
        invite_in: WebsiteInviteIn,
        websites_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    ) -> WebsiteResponse:
        website = await websites_repo.get_website_by_id(website_id=website_id)
        if not website:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NO_WEBSITE},
            )
        organiation: Organization = await website.awaitable_attrs.organization
        if not await user.is_admin_of(
            organization_id=organiation.id
        ) or not await user.is_admin_of_website(website_id=website_id):
            return response_4xx(
                status_code=HTTP_403_FORBIDDEN,
                context={"reason": constant.FAIL_NOT_ALLOWED},
            )
        if await self.is_already_member(email=invite_in.email, website=website):
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": constant.FAIL_USER_ALREADY_MEMBER},
            )
        invite: WebsiteInvite = await websites_repo.invite_to_website(
            website=website,
            email=invite_in.email,
            role=invite_in.role,
        )
        created_token = token.create_website_invitation_token(
            invite=invite, secret_key=secret_key
        )
        background_tasks.add_task(
            email.send_website_invitation_email,
            invite=invite,
            token=created_token.token,
        )
        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_INVITATION_EMAIL,
                "data": {},
            },
        )

    async def is_already_member(self, email: str, website: Website) -> bool:
        members = await website.awaitable_attrs.users
        for member in members:
            if member.user.email == email:
                return True
        return False

    @return_service
    async def accept_website_invite(
        self,
        token_in: token.InvitationTokenData,
        orgs_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
        user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        secret_key: str = "",
    ) -> WebsiteResponse:
        decoded_invite: token.TokenInvite = token.get_invite_from_token(
            token=token_in.token, secret_key=secret_key
        )
        org_invite: WebsiteInvite = await orgs_repo.get_website_invite(
            website_id=decoded_invite.website_id, email=decoded_invite.email
        )
        if not org_invite:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NO_ORGANIZATION_INVITE},
            )
        user = await user_repo.get_user_by_email(email=org_invite.email)
        if not user:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NEED_TO_SIGN_UP},
            )
        await orgs_repo.accept_website_invite(org_invite=org_invite, user=user)
        website = await org_invite.awaitable_attrs.website
        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_INVITATION_ACCEPT,
                "data": jsonable_encoder(WebsiteOutData.model_validate(website)),
            },
        )

    @return_service
    async def get_website_users(
        self,
        user: User,
        website_id: int,
        orgs_repo: WebsitesRepository = Depends(get_repository(WebsitesRepository)),
    ) -> WebsiteUserResponse:
        website: Website = await orgs_repo.get_website_by_id(website_id=website_id)
        if not website:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NO_ORGANIZATION},
            )
        if not await user.is_member_of(website.id):
            return response_4xx(
                status_code=HTTP_403_FORBIDDEN,
                context={"reason": constant.FAIL_NOT_ALLOWED},
            )
        org_users = await orgs_repo.get_website_users(website_id=website_id)
        data_users = []
        for org_user in org_users:
            user_data = await org_user.awaitable_attrs.user
            data_users.append(
                WebsiteUser(
                    **UserOutData.model_validate(user_data).model_dump(),
                    role=org_user.role,
                )
            )
        data = WebsiteUserOutData(
            **WebsiteOutData.model_validate(website).model_dump(),
            users=data_users,
        )
        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_GET_ORGANIZATION,
                "data": jsonable_encoder(data),
            },
        )
