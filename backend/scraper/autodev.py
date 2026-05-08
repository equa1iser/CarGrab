"""Auto.dev dealer inventory API poller.

Free tier: 1,000 calls/month.
Sign up at https://auto.dev to get a free API key.
Set AUTODEV_API_KEY in .env to enable this source.

Response notes:
- Always returns 20 records per page regardless of per_page param
- Use `page` param for pagination
- `priceUnformatted` is price in dollars (integer); `price` is formatted string
- `mileageUnformatted` is mileage as integer; `mileage` is formatted string
"""
import asyncio

import httpx
import structlog

from app.config import settings
from scraper.base import BaseSource, RawListing

log = structlog.get_logger()

_BASE = "https://auto.dev/api"
_PAGE_SIZE = 20   # API always returns 20 regardless of per_page
_DELAY = 1.0
_MAX_PAGES = 10   # cap per zip — 200 listings per search conserves free-tier quota

_SEARCHES = [
    {"zip": "10001", "radius": 150},  # New York area
    {"zip": "60601", "radius": 150},  # Chicago area
    {"zip": "90210", "radius": 150},  # LA area
    {"zip": "77001", "radius": 150},  # Houston area
    {"zip": "30301", "radius": 150},  # Atlanta area
]


class AutoDevPoller(BaseSource):
    name = "autodev"

    async def fetch(self) -> list[RawListing]:
        if not settings.autodev_api_key:
            log.warning("autodev_key_missing", msg="Set AUTODEV_API_KEY to enable Auto.dev")
            return []

        headers = {"X-API-Key": settings.autodev_api_key}
        results: list[RawListing] = []
        seen_ids: set[str] = set()

        async with httpx.AsyncClient(headers=headers, timeout=20) as client:
            for search in _SEARCHES:
                fetched = await _fetch_search(client, search, seen_ids)
                results.extend(fetched)
                await asyncio.sleep(_DELAY)

        log.info("autodev_fetch_complete", count=len(results))
        return results


async def _fetch_search(
    client: httpx.AsyncClient,
    search: dict,
    seen_ids: set[str],
) -> list[RawListing]:
    results: list[RawListing] = []
    page = 1

    while page <= _MAX_PAGES:
        try:
            resp = await client.get(
                f"{_BASE}/listings",
                params={**search, "page": page, "year_min": 2010, "price_min": 1000},
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            log.warning("autodev_fetch_error", search=search, page=page, error=str(exc))
            break

        records = data.get("records") or []
        if not records:
            break

        for item in records:
            listing_id = str(item.get("id") or item.get("vin") or "")
            if not listing_id or listing_id in seen_ids:
                continue
            seen_ids.add(listing_id)
            raw = _parse_item(item)
            if raw:
                results.append(raw)

        total = data.get("totalCount") or 0
        if page * _PAGE_SIZE >= total:
            break
        page += 1
        await asyncio.sleep(_DELAY)

    return results


def _parse_item(item: dict) -> RawListing | None:
    listing_id = str(item.get("id") or "")
    vin = item.get("vin")
    if not listing_id:
        return None

    # Price: prefer priceUnformatted (dollars int), fall back to parsing price string
    price_dollars = item.get("priceUnformatted") or item.get("basePrice")
    try:
        price_cents = int(float(price_dollars) * 100) if price_dollars else None
    except (ValueError, TypeError):
        price_cents = None

    # Mileage: prefer mileageUnformatted (integer)
    mileage = item.get("mileageUnformatted")
    if mileage is None:
        # Fall back to parsing formatted string "32,227 Miles"
        raw_mi = str(item.get("mileage") or "")
        digits = "".join(c for c in raw_mi if c.isdigit())
        mileage = int(digits) if digits else None

    # Photos
    photo_urls: list[str] = []
    primary = item.get("primaryPhotoUrl")
    if primary:
        photo_urls.append(primary)
    for p in item.get("photos") or []:
        if isinstance(p, str):
            photo_urls.append(p)
        elif isinstance(p, dict):
            u = p.get("url") or p.get("src") or ""
            if u:
                photo_urls.append(u)

    click_url = item.get("clickoffUrl")
    url = click_url or f"https://auto.dev/listings/{listing_id}"

    return RawListing(
        external_id=listing_id,
        url=url,
        source_name="autodev",
        price_cents=price_cents,
        mileage=mileage,
        year=item.get("year"),
        make=item.get("make"),
        model=item.get("model"),
        trim=item.get("trim"),
        vin=vin,
        condition=(item.get("condition") or "used").lower(),
        color_exterior=item.get("displayColor") or item.get("exteriorColor"),
        location_city=item.get("city"),
        location_state=item.get("state"),
        dealer_name=item.get("dealerName"),
        photo_urls=photo_urls,
        raw=item,
    )
