from sqlalchemy import Boolean, Column, Integer, String, text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship

from app.core import constant, security
from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel


class User(AsyncAttrs, RWModel, DateTimeModelMixin):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('users_id_seq'::regclass)"),
    )
    username = Column(String(32), nullable=False, unique=True)
    email = Column(String(256), nullable=False, unique=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    salt = Column(String(255), nullable=False)
    hashed_password = Column(String(256), nullable=True)

    # relationships
    organizations = relationship("OrganizationUser", back_populates="user")
    websites = relationship("WebsiteUser", back_populates="user")

    def check_password(self, password: str) -> bool:
        return security.verify_password(self.salt + password, self.hashed_password)

    def change_password(self, password: str) -> None:
        self.salt = security.generate_salt()
        self.hashed_password = security.get_password_hash(self.salt + password)

    async def is_member_of(self, organization_id: int) -> bool:
        orgs = await self.awaitable_attrs.organizations
        return any(org.organization_id == organization_id for org in orgs)

    async def is_admin_of(self, organization_id: int) -> bool:
        orgs = await self.awaitable_attrs.organizations
        return any(
            org.organization_id == organization_id
            and org.role == constant.ORGANIZATION_ADMIN
            for org in orgs
        )

    async def is_member_of_website(self, website_id: int) -> bool:
        websites = await self.awaitable_attrs.websites
        return any(org.website_id == website_id for org in websites)

    async def is_admin_of_website(self, website_id: int) -> bool:
        websites = await self.awaitable_attrs.websites
        return any(
            org.website_id == website_id and org.role == constant.WEBSITE_ADMIN
            for org in websites
        )
