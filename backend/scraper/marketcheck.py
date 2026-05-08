"""MarketCheck commercial API poller.

Requires MARKETCHECK_API_KEY in environment.
Gracefully returns [] if the key is not set — never crashes the worker.
Docs: https://marketcheck.com/apis
"""
import asyncio

import httpx
import structlog

from app.config import settings
from scraper.base import BaseSource, RawListing

log = structlog.get_logger()

_BASE = "https://mc-api.marketcheck.com/v2"
_ROWS = 100
_DELAY = 1.0  # 1 req/s courtesy rate limit


class MarketCheckPoller(BaseSource):
    name = "marketcheck"

    async def fetch(self) -> list[RawListing]:
        if not settings.marketcheck_api_key:
            log.warning("marketcheck_key_missing", msg="Set MARKETCHECK_API_KEY to enable MarketCheck")
            return []

        results: list[RawListing] = []
        start = 0
        async with httpx.AsyncClient(timeout=20) as client:
            while True:
                try:
                    resp = await client.get(
                        f"{_BASE}/search/car/active",
                        params={
                            "api_key": settings.marketcheck_api_key,
                            "rows": _ROWS,
                            "start": start,
                            "country": "US",
                            "price_min": 500,
                            "year_min": 1990,
                            "fields": (
                                "id,vin,price,miles,year,make,model,trim,"
                                "exterior_color,interior_color,city,state,zip,"
                                "dealer,media,vdp_url,dom,condition"
                            ),
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                except Exception as exc:
                    log.warning("marketcheck_fetch_error", start=start, error=str(exc))
                    break

                listings = data.get("listings") or []
                if not listings:
                    break

                for item in listings:
                    raw = _parse_item(item)
                    if raw:
                        results.append(raw)

                start += _ROWS
                if len(listings) < _ROWS:
                    break
                await asyncio.sleep(_DELAY)

        log.info("marketcheck_fetch_complete", count=len(results))
        return results


def _parse_item(item: dict) -> RawListing | None:
    listing_id = item.get("id")
    url = item.get("vdp_url")
    if not listing_id or not url:
        return None

    price_raw = item.get("price")
    try:
        price_cents = int(float(price_raw) * 100) if price_raw else None
    except (ValueError, TypeError):
        price_cents = None

    media = item.get("media") or {}
    photo_urls: list[str] = media.get("photo_links") or []

    dealer = item.get("dealer") or {}

    return RawListing(
        external_id=str(listing_id),
        url=url,
        source_name="marketcheck",
        price_cents=price_cents,
        mileage=item.get("miles"),
        year=item.get("year"),
        make=item.get("make"),
        model=item.get("model"),
        trim=item.get("trim"),
        vin=item.get("vin"),
        condition=(item.get("condition") or "used").lower(),
        color_exterior=item.get("exterior_color"),
        color_interior=item.get("interior_color"),
        location_city=item.get("city"),
        location_state=item.get("state"),
        location_zip=item.get("zip"),
        dealer_name=dealer.get("name"),
        photo_urls=photo_urls,
        raw=item,
    )
