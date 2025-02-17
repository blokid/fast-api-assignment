from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship

from app.models.common import DateTimeModelMixin
from app.models.rwmodel import RWModel


class Website(AsyncAttrs, RWModel, DateTimeModelMixin):
    __tablename__ = "websites"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('websites_id_seq'::regclass)"),
    )
    name = Column(String(64), nullable=False, unique=True)
    url = Column(String(256), nullable=False, unique=True)
    description = Column(String(256), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # relationships
    users = relationship("WebsiteUser", back_populates="website")
    invites = relationship("WebsiteInvite", back_populates="website")
    organization = relationship("Organization", back_populates="websites")


class WebsiteUser(AsyncAttrs, RWModel, DateTimeModelMixin):
    __tablename__ = "website_users"

    website_id = Column(
        Integer, ForeignKey("websites.id"), nullable=False, primary_key=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, primary_key=True)
    role = Column(String(16), nullable=False)

    # relationships
    website = relationship("Website", back_populates="users")
    user = relationship("User", back_populates="websites")


class WebsiteInvite(AsyncAttrs, RWModel, DateTimeModelMixin):
    __tablename__ = "website_invites"

    website_id = Column(
        Integer, ForeignKey("websites.id"), nullable=False, primary_key=True
    )
    email = Column(String(256), nullable=False, primary_key=True)
    role = Column(String(16), nullable=False)
    is_accepted = Column(Boolean, nullable=False, default=False)

    # relationships
    website = relationship("Website", back_populates="invites")
