import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship

from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel


class Organization(AsyncAttrs, RWModel, DateTimeModelMixin):
    __tablename__ = "organizations"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('organizations_id_seq'::regclass)"),
    )
    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(256), nullable=True)

    # relationships
    users = relationship("OrganizationUser", back_populates="organization")
    invites = relationship("OrganizationInvite", back_populates="organization")

    @staticmethod
    def generate_random_name() -> str:
        return str(uuid.uuid4()).replace("-", "")[:10]


class OrganizationUser(RWModel, DateTimeModelMixin):
    __tablename__ = "organization_users"

    organization_id = Column(
        Integer, ForeignKey("organizations.id"), nullable=False, primary_key=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, primary_key=True)
    role = Column(String(16), nullable=False)

    # relationships
    organization = relationship("Organization", back_populates="users")
    user = relationship("User", back_populates="organizations")


class OrganizationInvite(AsyncAttrs, RWModel, DateTimeModelMixin):
    __tablename__ = "organization_invites"

    organization_id = Column(
        Integer, ForeignKey("organizations.id"), nullable=False, primary_key=True
    )
    email = Column(String(256), nullable=False, primary_key=True)
    role = Column(String(16), nullable=False)
    is_accepted = Column(Boolean, nullable=False, default=False)

    # relationships
    organization = relationship("Organization", back_populates="invites")
