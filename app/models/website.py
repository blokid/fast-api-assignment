from sqlalchemy import Column, Integer, String, ForeignKey, Enum, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.models.common import DateTimeModelMixin
from app.models.user import User
from app.models.organization import Organization
from app.models.rwmodel import RWModel
import enum


class WebsiteRoleEnum(str, enum.Enum):
    admin = "admin"
    member = "member"


class Website(RWModel, DateTimeModelMixin):
    __tablename__ = "websites"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('websites_id_seq'::regclass)"),
    )
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    url = Column(String(2083), nullable=False, unique=True)

    members = relationship(
        "WebsiteMembership",
        back_populates="website",
        cascade="all, delete-orphan",
    )
    organization = relationship("Organization", back_populates="websites")


class WebsiteMembership(RWModel, DateTimeModelMixin):
    __tablename__ = "website_memberships"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('website_memberships_id_seq'::regclass)"),
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    website_id = Column(
        Integer, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(
        Enum(WebsiteRoleEnum, name="website_role_enum"),
        nullable=False,
        default=WebsiteRoleEnum.member,
    )
    joined_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    deleted_at = None

    user = relationship("User", back_populates="websites")
    website = relationship("Website", back_populates="members")


# Add relationship to User model
User.websites = relationship(
    "WebsiteMembership", back_populates="user", cascade="all, delete-orphan"
)

# Add relationship to Organization model
Organization.websites = relationship(
    "Website", back_populates="organization", cascade="all, delete-orphan"
)
