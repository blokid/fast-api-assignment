from app.api.v1.organizations import organizations
from fastapi import APIRouter
from app.api.v1.organizations import (
    organizations,
    organization_memberships,
    websites,
    website_memberships,
)
from app.api.v1 import auth, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(
    organization_memberships.router,
    prefix="/organizations/{organization_id}/memberships",
    tags=["organization-membership"],
)

api_router.include_router(
    websites.router,
    prefix="/websites",
    tags=["website"],
)

api_router.include_router(
    website_memberships.router,
    prefix="/websites/{website_id}/memberships",
    tags=["website-membership"],
)
