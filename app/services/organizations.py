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
from app.models import OrganizationInvite, User
from app.schemas.organization import (
    OrganizationInCreate,
    OrganizationInviteIn,
    OrganizationOutData,
    OrganizationResponse,
)
from app.services.base import BaseService
from app.utils import (
    email,
    response_4xx,
    return_service,
)

logger = logging.getLogger(__name__)


class OrganizationsService(BaseService):

    @return_service
    async def create_organization(
        self,
        org_in: OrganizationInCreate,
        user: User,
        orgs_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> OrganizationResponse:
        duplicate_org = await orgs_repo.get_organization_by_name(name=org_in.name)

        if duplicate_org:
            return response_4xx(
                status_code=HTTP_400_BAD_REQUEST,
                context={"reason": constant.FAIL_VALIDATION_ORGANIZATION_DUPLICATED},
            )

        created_org = await orgs_repo.create_organization(org_in=org_in, user=user)

        return dict(
            status_code=HTTP_201_CREATED,
            content={
                "message": constant.SUCCESS_CREATE_ORGANIZATION,
                "data": jsonable_encoder(
                    OrganizationOutData.model_validate(created_org)
                ),
            },
        )

    @return_service
    async def get_organizations(
        self,
        orgs_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> OrganizationResponse:
        organizations = await orgs_repo.get_organizations()

        if not organizations:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NO_ORGANIZATION},
            )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_GET_ORGANIZATION,
                "data": jsonable_encoder(
                    [OrganizationOutData.model_validate(org) for org in organizations]
                ),
            },
        )

    @return_service
    async def get_organization(
        self,
        user: User,
        organization_id: int,
        orgs_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> OrganizationResponse:
        organization = await orgs_repo.get_organization_by_id(
            organization_id=organization_id
        )

        if not organization:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NO_ORGANIZATION},
            )
        if not await user.is_member_of(organization.id):
            return response_4xx(
                status_code=HTTP_403_FORBIDDEN,
                context={"reason": constant.FAIL_NOT_ALLOWED},
            )

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_GET_ORGANIZATION,
                "data": jsonable_encoder(
                    OrganizationOutData.model_validate(organization)
                ),
            },
        )

    @return_service
    async def delete_organization(
        self,
        user: User,
        organization_id: int,
        orgs_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> OrganizationResponse:
        organization = await orgs_repo.get_organization_by_id(
            organization_id=organization_id
        )

        if not organization:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NO_ORGANIZATION},
            )
        if not await user.is_admin_of(organization.id):
            return response_4xx(
                status_code=HTTP_403_FORBIDDEN,
                context={"reason": constant.FAIL_NOT_ALLOWED},
            )

        await orgs_repo.delete_organization(organization_id=organization_id)

        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_DELETE_ORGANIZATION,
            },
        )

    @return_service
    async def invite_to_organization(
        self,
        user: User,
        organization_id: int,
        background_tasks: BackgroundTasks,
        secret_key: str,
        invite_in: OrganizationInviteIn,
        orgs_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
    ) -> OrganizationResponse:
        organization = await orgs_repo.get_organization_by_id(
            organization_id=organization_id
        )

        if not organization:
            return response_4xx(
                status_code=HTTP_404_NOT_FOUND,
                context={"reason": constant.FAIL_NO_ORGANIZATION},
            )
        if not await user.is_admin_of(organization.id):
            return response_4xx(
                status_code=HTTP_403_FORBIDDEN,
                context={"reason": constant.FAIL_NOT_ALLOWED},
            )

        invite: OrganizationInvite = await orgs_repo.invite_to_organization(
            organization=organization,
            email=invite_in.email,
            role=invite_in.role,
        )
        created_token = token.create_org_invitation_token(
            invite=invite, secret_key=secret_key
        )
        background_tasks.add_task(
            email.send_invitation_email,
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

    @return_service
    async def accept_organization_invite(
        self,
        token_in: token.InvitationTokenData,
        orgs_repo: OrganizationsRepository = Depends(
            get_repository(OrganizationsRepository)
        ),
        user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        secret_key: str = "",
    ) -> OrganizationResponse:
        decoded_invite: token.TokenInvite = token.get_invite_from_token(
            token=token_in.token, secret_key=secret_key
        )
        org_invite: OrganizationInvite = await orgs_repo.get_organization_invite(
            organization_id=decoded_invite.organization_id, email=decoded_invite.email
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
        await orgs_repo.accept_organization_invite(org_invite=org_invite)
        organization = await org_invite.awaitable_attrs.organization
        return dict(
            status_code=HTTP_200_OK,
            content={
                "message": constant.SUCCESS_INVITATION_ACCEPT,
                "data": jsonable_encoder(
                    OrganizationOutData.model_validate(organization)
                ),
            },
        )
