from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    constr,
    validator,
    constr,
    ValidationError,
)

from app.core import security
from app.schemas.message import ApiResponse


class UserBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    username: str
    email: str
    updated_at: datetime | None = None


class UserInDB(UserBase):
    salt: str | None = None
    hashed_password: str | None = None

    def check_password(self, password: str) -> bool:
        return security.verify_password(self.salt + password, self.hashed_password)

    def change_password(self, password: str) -> None:
        self.salt = security.generate_salt()
        self.hashed_password = security.get_password_hash(self.salt + password)


class UserInSignIn(BaseModel):
    password: str
    email: str


class UserInVerification(BaseModel):
    verification_token: str


class UserInCreate(BaseModel):
    username: constr(min_length=5, max_length=20)
    password: constr(min_length=8, max_length=128)  # Minimum 8 chars
    email: EmailStr

    @validator("password")
    def validate_password(cls, value):
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class UserInUpdate(UserInCreate):
    username: str | None = None
    password: str | None = None
    email: str | None = None


class UsersFilters(BaseModel):
    skip: int | None = 0
    limit: int | None = 100


class UserTokenData(BaseModel):
    access_token: str | None = None
    token_type: str | None = None


class UserAuthOutData(UserBase):
    token: UserTokenData | None = None


class UserOutData(UserBase):
    pass


class UserResponse(ApiResponse):
    message: str = "User API Response"
    data: UserOutData | list[UserOutData] | UserAuthOutData
    detail: dict[str, Any] | None = {"key": "val"}


class SignupResponse(ApiResponse):
    message: str = "User Signup Response"
