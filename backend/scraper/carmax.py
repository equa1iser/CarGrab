"""CarMax unofficial JSON API poller.

CarMax exposes an internal search endpoint that returns structured JSON.
We poll it with reasonable delays. Disable immediately on any legal contact.
"""
import asyncio

import httpx
import structlog

from scraper.base import BaseSource, RawListing

log = structlog.get_logger()

_SEARCH_URL = "https://www.carmax.com/cars/api/search/run"
_HEADERS = {
    "User-Agent": "CarGrab/1.0 (research aggregator; contact: admin@cargrab.example.com)",
    "Accept": "application/json",
    "Referer": "https://www.carmax.com/cars",
}
_BATCH = 24
_DELAY = 2.0  # seconds between paginated requests
_MAX_PAGES = 50  # safety cap (~1,200 listings per poll cycle)

# Sample zip codes spread across US regions for broader coverage
_ZIP_CODES = ["10001", "90210", "60601", "77001", "85001", "98101", "30301", "33101"]


class CarMaxPoller(BaseSource):
    name = "carmax"

    async def fetch(self) -> list[RawListing]:
        results: list[RawListing] = []
        async with httpx.AsyncClient(headers=_HEADERS, timeout=15, follow_redirects=True) as client:
            for zip_code in _ZIP_CODES:
                listings = await self._fetch_zip(client, zip_code)
                results.extend(listings)
                await asyncio.sleep(_DELAY)
        log.info("carmax_fetch_complete", count=len(results))
        return results

    async def _fetch_zip(self, client: httpx.AsyncClient, zip_code: str) -> list[RawListing]:
        results: list[RawListing] = []
        skip = 0
        for _ in range(_MAX_PAGES):
            try:
                resp = await client.post(
                    _SEARCH_URL,
                    json={"zipCode": zip_code, "take": _BATCH, "skip": skip, "sortBy": "listed-date-desc"},
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                log.warning("carmax_fetch_error", zip=zip_code, skip=skip, error=str(exc))
                break

            items = data.get("items") or data.get("Vehicles") or []
            if not items:
                break

            for item in items:
                raw = _parse_item(item, zip_code)
                if raw:
                    results.append(raw)

            skip += _BATCH
            if skip >= (data.get("totalCount") or 0):
                break
            await asyncio.sleep(_DELAY)

        return results


def _parse_item(item: dict, zip_code: str) -> RawListing | None:
    stock = item.get("stockNumber") or item.get("StockNumber")
    if not stock:
        return None

    price_raw = item.get("price") or item.get("ListPrice") or 0
    try:
        price_cents = int(float(price_raw) * 100)
    except (ValueError, TypeError):
        price_cents = None

    photos: list[str] = []
    primary = item.get("primaryPhotoUrl") or item.get("PrimaryPhotoUrl")
    if primary:
        photos.append(primary)
    additional = item.get("additionalPhotoUrls") or []
    photos.extend(additional)

    return RawListing(
        external_id=str(stock),
        url=f"https://www.carmax.com/car/{stock}",
        source_name="carmax",
        price_cents=price_cents,
        mileage=item.get("mileage") or item.get("Mileage"),
        year=item.get("year") or item.get("Year"),
        make=item.get("make") or item.get("Make"),
        model=item.get("model") or item.get("Model"),
        trim=item.get("trim") or item.get("Trim"),
        vin=item.get("vin") or item.get("Vin"),
        condition="used",
        location_city=item.get("storeCity") or item.get("StoreCity"),
        location_state=item.get("storeState") or item.get("StoreState"),
        dealer_name="CarMax",
        photo_urls=photos,
        raw=item,
    )
