# website_membership.py

from pydantic import BaseModel
from typing import Optional, Union, List, Any
from datetime import datetime
from app.models.website import WebsiteRoleEnum
from app.schemas.message import ApiResponse


# Website Membership Schemas
class WebsiteMembershipBase(BaseModel):
    user_id: int
    website_id: int
    role: WebsiteRoleEnum


class WebsiteMembershipInCreate(BaseModel):
    user_id: int
    role: WebsiteRoleEnum


class WebsiteMembershipInUpdate(BaseModel):
    role: Optional[WebsiteRoleEnum] = None


class WebsiteMembershipOutData(WebsiteMembershipBase):
    id: int
    joined_at: datetime


class WebsiteMembershipResponse(ApiResponse):
    message: str = "Website Membership Response"
    data: Union[WebsiteMembershipOutData, List[WebsiteMembershipOutData]]
    detail: dict[str, Any] | None = {"key": "val"}
