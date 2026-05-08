"""eBay Motors listings poller using the eBay Browse API.

Free developer account: https://developer.ebay.com/
Register an app to get App ID (Client ID) and Cert ID (Client Secret).
Set EBAY_APP_ID and EBAY_CERT_ID in .env to enable this source.

Category 6001 = eBay Motors > Cars & Trucks.
"""
import asyncio
import base64
import re
import time

import httpx
import structlog

from app.config import settings
from scraper.base import BaseSource, RawListing

log = structlog.get_logger()

_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
_CATEGORY_ID = "6001"  # Cars & Trucks
_LIMIT = 200
_DELAY = 0.5

# Search queries to cover a wide range of listings
_QUERIES = [
    "used car sedan 2018 2019 2020",
    "used truck pickup 2018 2019 2020",
    "used SUV crossover 2018 2019 2020",
    "used car sedan 2021 2022 2023",
    "used SUV crossover 2021 2022 2023",
]

# Module-level token cache
_token_cache: dict = {"access_token": None, "expires_at": 0}


async def _get_access_token(client: httpx.AsyncClient) -> str | None:
    """Obtain an OAuth 2.0 client credentials token, cached until expiry."""
    now = time.time()
    if _token_cache["access_token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["access_token"]

    credentials = base64.b64encode(
        f"{settings.ebay_app_id}:{settings.ebay_cert_id}".encode()
    ).decode()

    try:
        resp = await client.post(
            _TOKEN_URL,
            headers={"Authorization": f"Basic {credentials}"},
            data={
                "grant_type": "client_credentials",
                "scope": "https://api.ebay.com/oauth/api_scope",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        _token_cache["access_token"] = data["access_token"]
        _token_cache["expires_at"] = now + data.get("expires_in", 7200)
        log.info("ebay_token_obtained")
        return _token_cache["access_token"]
    except Exception as exc:
        log.warning("ebay_token_error", error=str(exc))
        return None


class EBayMotorsPoller(BaseSource):
    name = "ebay"

    async def fetch(self) -> list[RawListing]:
        if not settings.ebay_app_id or not settings.ebay_cert_id:
            log.warning("ebay_keys_missing", msg="Set EBAY_APP_ID and EBAY_CERT_ID to enable eBay Motors")
            return []

        results: list[RawListing] = []
        seen_ids: set[str] = set()

        async with httpx.AsyncClient(timeout=20) as client:
            token = await _get_access_token(client)
            if not token:
                return []

            headers = {
                "Authorization": f"Bearer {token}",
                "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
                "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=<eCampaignId>,affiliateReferenceId=<eReferenceId>",
            }

            for query in _QUERIES:
                offset = 0
                while True:
                    try:
                        resp = await client.get(
                            _SEARCH_URL,
                            headers=headers,
                            params={
                                "q": query,
                                "category_ids": _CATEGORY_ID,
                                "sort": "newlyListed",
                                "limit": _LIMIT,
                                "offset": offset,
                                "filter": "conditions:{USED},deliveryCountry:US,price:[500..200000]",
                            },
                        )
                        resp.raise_for_status()
                        data = resp.json()
                    except Exception as exc:
                        log.warning("ebay_fetch_error", query=query, offset=offset, error=str(exc))
                        break

                    items = data.get("itemSummaries") or []
                    if not items:
                        break

                    for item in items:
                        item_id = item.get("itemId", "")
                        if not item_id or item_id in seen_ids:
                            continue
                        seen_ids.add(item_id)
                        raw = _parse_item(item)
                        if raw:
                            results.append(raw)

                    total = data.get("total", 0)
                    offset += _LIMIT
                    if offset >= min(total, 1000):  # cap at 1000 per query to preserve free tier
                        break
                    await asyncio.sleep(_DELAY)

                await asyncio.sleep(_DELAY)

        log.info("ebay_fetch_complete", count=len(results))
        return results


def _parse_specifics(specifics: list[dict]) -> dict[str, str]:
    """Flatten eBay itemSpecifics list into a plain dict."""
    result = {}
    for spec in specifics or []:
        key = spec.get("name", "").lower().replace(" ", "_")
        values = spec.get("values") or []
        if values:
            result[key] = values[0]
    return result


def _parse_mileage(value: str | None) -> int | None:
    if not value:
        return None
    digits = re.sub(r"[^\d]", "", str(value))
    return int(digits) if digits else None


def _parse_item(item: dict) -> RawListing | None:
    item_id = item.get("itemId")
    if not item_id:
        return None

    specs = _parse_specifics(item.get("itemSpecifics") or [])

    # Year: prefer specs, fall back to parsing title
    year_raw = specs.get("year")
    year: int | None = None
    if year_raw:
        try:
            year = int(year_raw)
        except ValueError:
            pass
    if not year:
        title = item.get("title", "")
        match = re.search(r"\b(19|20)\d{2}\b", title)
        if match:
            year = int(match.group())

    make = specs.get("make")
    model = specs.get("model")
    trim = specs.get("trim_level") or specs.get("trim")
    vin = specs.get("vin")
    color_ext = specs.get("exterior_color") or specs.get("color")
    mileage = _parse_mileage(specs.get("mileage"))

    price_info = item.get("price") or {}
    try:
        price_cents = int(float(price_info.get("value", 0)) * 100) or None
    except (ValueError, TypeError):
        price_cents = None

    location = item.get("itemLocation") or {}
    city = location.get("city")
    state = location.get("stateOrProvince")

    primary_photo = (item.get("image") or {}).get("imageUrl")
    extra_photos = [(p.get("imageUrl") or "") for p in (item.get("additionalImages") or [])]
    photo_urls = [u for u in ([primary_photo] + extra_photos) if u]

    title = item.get("title", "")
    url = item.get("itemWebUrl", f"https://www.ebay.com/itm/{item_id}")

    # Skip listings that clearly aren't cars (parts, accessories)
    if not year and not make:
        return None

    return RawListing(
        external_id=str(item_id),
        url=url,
        source_name="ebay",
        price_cents=price_cents,
        mileage=mileage,
        year=year,
        make=make,
        model=model,
        trim=trim,
        vin=vin,
        condition="used",
        color_exterior=color_ext,
        location_city=city,
        location_state=state,
        dealer_name=None,  # eBay mixes private sellers and dealers; can't distinguish cleanly
        description=title,
        photo_urls=photo_urls,
        raw=item,
    )
