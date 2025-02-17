from typing import Any

from app.schemas.message import ApiResponse
from app.schemas.organization import OrganizationBase
from app.schemas.user import UserBase


class OrganizationUser(UserBase):
    role: str


class OrganizationUserBase(OrganizationBase):
    users: list[OrganizationUser]


class OrganizationUserOutData(OrganizationUserBase):
    pass


class OrganizationUserResponse(ApiResponse):
    message: str = "Organization API Response"
    data: OrganizationUserOutData | list[OrganizationUserOutData]
    detail: dict[str, Any] | None = {"key": "val"}
