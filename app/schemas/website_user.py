from typing import Any

from app.schemas.message import ApiResponse
from app.schemas.user import UserBase
from app.schemas.website import WebsiteBase


class WebsiteUser(UserBase):
    role: str


class UserWebsite(WebsiteBase):
    role: str


class WebsiteUserBase(WebsiteBase):
    users: list[WebsiteUser]


class UserWebsiteBase(UserBase):
    websites: list[UserWebsite]


class WebsiteUserOutData(WebsiteUserBase):
    pass


class UserWebsiteOutData(UserWebsiteBase):
    pass


class WebsiteUserResponse(ApiResponse):
    message: str = "Website API Response"
    data: (
        WebsiteUserOutData
        | list[WebsiteUserOutData]
        | UserWebsiteOutData
        | list[UserWebsiteOutData]
    )
    detail: dict[str, Any] | None = {"key": "val"}
