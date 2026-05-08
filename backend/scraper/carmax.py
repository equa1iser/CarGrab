"""CarMax unofficial JSON API poller.

CarMax exposes an internal search endpoint that returns structured JSON, but
the site is protected by Akamai Bot Manager which requires JavaScript execution.
We use Playwright (headless Chromium) to navigate to the search page and make
the API call from within the browser context (same-origin), bypassing Akamai.

Disable immediately on any legal contact.
"""
import asyncio

import structlog
from playwright.async_api import async_playwright

from scraper.base import BaseSource, RawListing

log = structlog.get_logger()

_BASE_URL = "https://www.carmax.com"
_SEARCH_URL = "https://www.carmax.com/cars/api/search/run"
_BATCH = 24
_DELAY = 3.0

# Fewer zip codes to keep polling time manageable (Playwright is slower than httpx)
_ZIP_CODES = ["10001", "90210", "60601", "77001", "30301"]


async def _fetch_zip_via_browser(zip_code: str) -> list[dict]:
    """Navigate to CarMax search, then call the API from within the browser context."""
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                ],
            )
            ctx = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="en-US",
                timezone_id="America/New_York",
                viewport={"width": 1920, "height": 1080},
            )
            await ctx.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            page = await ctx.new_page()
            await page.goto(f"{_BASE_URL}/cars?zip={zip_code}", wait_until="networkidle", timeout=45000)
            await page.wait_for_timeout(3000)

            # Make the search API call from inside the browser (same-origin, carries cookies)
            result = await page.evaluate(
                """
                async ([url, zip, take]) => {
                    try {
                        const r = await fetch(url, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
                            body: JSON.stringify({zipCode: zip, take: take, skip: 0, sortBy: 'listed-date-desc'})
                        });
                        const ct = r.headers.get('content-type') || '';
                        if (!r.ok || !ct.includes('json')) {
                            return {error: r.status, ct: ct};
                        }
                        return await r.json();
                    } catch(e) {
                        return {error: String(e)};
                    }
                }
                """,
                [_SEARCH_URL, zip_code, _BATCH],
            )

            await browser.close()

            if isinstance(result, dict) and "error" in result:
                log.warning("carmax_browser_api_error", zip=zip_code, error=result.get("error"))
                return []

            items = result.get("items") or result.get("Vehicles") or []
            log.info("carmax_zip_fetched", zip=zip_code, count=len(items))
            return items

    except Exception as exc:
        log.warning("carmax_playwright_error", zip=zip_code, error=str(exc))
        return []


class CarMaxPoller(BaseSource):
    name = "carmax"

    async def fetch(self) -> list[RawListing]:
        results: list[RawListing] = []
        for zip_code in _ZIP_CODES:
            items = await _fetch_zip_via_browser(zip_code)
            for item in items:
                raw = _parse_item(item, zip_code)
                if raw:
                    results.append(raw)
            await asyncio.sleep(_DELAY)

        log.info("carmax_fetch_complete", count=len(results))
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
