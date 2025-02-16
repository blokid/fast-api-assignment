from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.message import ApiResponse


class OrganizationBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    name: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class OrganizationInDB(OrganizationBase):
    pass


class OrganizationInCreate(BaseModel):
    name: str
    description: str | None = None


class OrganizationInUpdate(OrganizationInCreate):
    name: str | None = None
    description: str | None = None


class OrganizationOutData(OrganizationBase):
    pass


class OrganizationResponse(ApiResponse):
    message: str = "Organization API Response"
    data: OrganizationOutData | list[OrganizationOutData]
    detail: dict[str, Any] | None = {"key": "val"}
