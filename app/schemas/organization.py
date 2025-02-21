from datetime import datetime
from typing import Any, Optional, List, Union
from pydantic import BaseModel
from app.schemas.message import ApiResponse


class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class OrganizationInCreate(OrganizationBase):
    pass


class OrganizationsFilters(BaseModel):
    skip: int | None = 0
    limit: int | None = 100


class OrganizationInUpdate(OrganizationBase):
    name: Optional[str] = None
    description: Optional[str] = None


class OrganizationInDB(OrganizationBase):
    id: int | None = None


class OrganizationOutData(OrganizationBase):
    id: int | None = None


class OrganizationResponse(ApiResponse):
    message: str = "Organization API Response"
    data: Union[OrganizationOutData, List[OrganizationOutData]]
    detail: dict[str, Any] | None = {"key": "val"}


class MembershipOutData(BaseModel):
    id: int
    user_id: int
    role: str
    created_at: datetime | None


class OrganizationDetailOut(OrganizationOutData):
    members: List[MembershipOutData] = []
