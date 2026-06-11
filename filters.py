"""Region and sector filtering."""
import config


def region_for(country: str | None) -> str | None:
    if not country:
        return None
    for region, countries in config.REGIONS.items():
        if country in countries:
            return region
    return None


def matches_sector(tender: dict) -> bool:
    """Accept if civil-works procurement group, or if title/excerpt hits a keyword."""
    if tender.get("procurement_group") in config.ACCEPT_PROCUREMENT_GROUPS:
        return True
    haystack = " ".join(
        filter(None, [tender.get("title", ""), tender.get("raw_excerpt", ""),
                      tender.get("project_name", "")])
    ).lower()
    return any(kw in haystack for kw in config.SECTOR_KEYWORDS)


def accept(tender: dict) -> bool:
    if tender.get("notice_type") in config.SKIP_NOTICE_TYPES:
        return False
    region = region_for(tender.get("country"))
    if region is None:
        return False
    tender["region"] = region
    return matches_sector(tender)
