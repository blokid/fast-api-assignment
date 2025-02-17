from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from app.core import constant
from app.schemas.message import ApiResponse


class WebsiteBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    name: str
    url: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class WebsiteInDB(WebsiteBase):
    pass


class WebsiteInCreate(BaseModel):
    name: str
    url: str
    description: str | None = None


class WebsiteInUpdate(WebsiteInCreate):
    name: str | None = None
    url: str | None = None
    description: str | None = None


class WebsiteOutData(WebsiteBase):
    pass


class WebsiteResponse(ApiResponse):
    message: str = "Website API Response"
    data: WebsiteOutData | list[WebsiteOutData]
    detail: dict[str, Any] | None = {"key": "val"}


class WebsiteInviteIn(BaseModel):
    email: str
    role: str

    @field_validator("role")
    def validate_role(cls, v: str) -> str:
        roles = [constant.WEBSITE_ADMIN, constant.WEBSITE_MEMBER]
        if v not in roles:
            raise ValueError(f"role must be one of {', '.join(map(repr, roles))}")
        return v
