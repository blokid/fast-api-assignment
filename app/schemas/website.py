# website.py

from datetime import datetime
from typing import Any, Optional, List, Union
from pydantic import BaseModel, constr, validator
from app.schemas.message import ApiResponse
from app.schemas.website_membership import WebsiteMembershipOutData


# Website Schemas
class WebsiteBase(BaseModel):
    name: constr(min_length=3, max_length=100)
    url: str
    description: Optional[str] = None

    @validator("url")
    def validate_url(cls, value):
        if not value.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return value


class WebsiteInCreate(WebsiteBase):
    pass


class WebsitesFilters(BaseModel):
    organization_id: Optional[int] = None
    skip: int | None = 0
    limit: int | None = 100


class WebsiteInUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None


class WebsiteInDB(WebsiteBase):
    id: int | None = None
    organization_id: int


class WebsiteOutData(WebsiteBase):
    id: int
    organization_id: int


class WebsiteResponse(ApiResponse):
    message: str = "Website API Response"
    data: Union[WebsiteOutData, List[WebsiteOutData]]
    detail: dict[str, Any] | None = {"key": "val"}


class WebsiteDetailOut(WebsiteOutData):
    members: List[WebsiteMembershipOutData] = []
