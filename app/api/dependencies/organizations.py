from app.schemas.organization import OrganizationsFilters


def get_organizations_filters(
    skip: int | None = 0, limit: int | None = 100
) -> OrganizationsFilters:
    return OrganizationsFilters(
        skip=skip,
        limit=limit,
    )
