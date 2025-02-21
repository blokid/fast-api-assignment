# organization_membership.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.organization import OrganizationRoleEnum
from app.schemas.message import ApiResponse
from typing import Any


class OrganizationMembershipBase(BaseModel):
    user_id: int
    organization_id: int
    role: OrganizationRoleEnum


class OrganizationMembershipInCreate(BaseModel):
    user_id: int
    role: OrganizationRoleEnum


class OrganizationMembershipInDB(OrganizationMembershipBase):
    id: Optional[int] = None
    joined_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class OrganizationMembershipInUpdate(BaseModel):
    role: Optional[OrganizationRoleEnum] = None


class OrganizationMembershipOutData(OrganizationMembershipBase):
    id: int
    joined_at: datetime


class OrganizationMembershipResponse(ApiResponse):
    message: str = "Org Membership Response"
    data: OrganizationMembershipOutData | list[OrganizationMembershipOutData]
    detail: dict[str, Any] | None = {"key": "val"}
