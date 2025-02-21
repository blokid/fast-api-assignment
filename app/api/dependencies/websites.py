from app.schemas.website import WebsitesFilters


def get_websites_filters(
    skip: int | None = 0, limit: int | None = 100
) -> WebsitesFilters:
    return WebsitesFilters(
        skip=skip,
        limit=limit,
    )
