from sqlalchemy import Column, Integer, String, ForeignKey, Enum, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.models.common import DateTimeModelMixin
from app.models.user import User
from app.models.rwmodel import RWModel
import enum


class OrganizationRoleEnum(str, enum.Enum):
    admin = "admin"
    member = "member"


class Organization(RWModel, DateTimeModelMixin):
    __tablename__ = "organizations"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('organizations_id_seq'::regclass)"),
    )
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=True)

    members = relationship(
        "OrganizationMembership",
        back_populates="organization",
        cascade="all, delete-orphan",
    )


class OrganizationMembership(RWModel, DateTimeModelMixin):
    __tablename__ = "organization_memberships"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('organization_memberships_id_seq'::regclass)"),
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(
        Enum(OrganizationRoleEnum, name="organization_role_enum"),
        nullable=False,
        default=OrganizationRoleEnum.member,
    )
    joined_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    deleted_at = None
    user = relationship("User", back_populates="organizations")
    organization = relationship("Organization", back_populates="members")


User.organizations = relationship(
    "OrganizationMembership", back_populates="user", cascade="all, delete-orphan"
)
