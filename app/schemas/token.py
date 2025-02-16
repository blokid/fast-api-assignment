from datetime import datetime

from pydantic import BaseModel


class TokenBase(BaseModel):
    exp: datetime
    sub: str


class TokenUser(BaseModel):
    id: int
    username: str
    email: str


class TokenVerify(BaseModel):
    email: str


class TokenInvite(BaseModel):
    organization_id: int
    email: str
