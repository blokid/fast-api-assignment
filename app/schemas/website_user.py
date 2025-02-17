from typing import Any

from app.schemas.message import ApiResponse
from app.schemas.user import UserBase
from app.schemas.website import WebsiteBase


class WebsiteUser(UserBase):
    role: str


class WebsiteUserBase(WebsiteBase):
    users: list[WebsiteUser]


class WebsiteUserOutData(WebsiteUserBase):
    pass


class WebsiteUserResponse(ApiResponse):
    message: str = "Website API Response"
    data: WebsiteUserOutData | list[WebsiteUserOutData]
    detail: dict[str, Any] | None = {"key": "val"}
