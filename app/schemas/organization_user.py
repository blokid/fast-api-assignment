from typing import Any

from app.schemas.message import ApiResponse
from app.schemas.organization import OrganizationBase
from app.schemas.user import UserBase


class OrganizationUser(UserBase):
    role: str


class UserOrganization(OrganizationBase):
    role: str


class UserOrganizationBase(UserBase):
    organizations: list[UserOrganization]


class OrganizationUserBase(OrganizationBase):
    users: list[OrganizationUser]


class OrganizationUserOutData(OrganizationUserBase):
    pass


class UserOrganizationOutData(UserOrganizationBase):
    pass


class OrganizationUserResponse(ApiResponse):
    message: str = "Organization API Response"
    data: (
        OrganizationUserOutData
        | list[OrganizationUserOutData]
        | UserOrganizationOutData
        | list[UserOrganizationOutData]
    )
    detail: dict[str, Any] | None = {"key": "val"}
