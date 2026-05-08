"""Celery tasks: poll sources, upsert listings, trigger price alerts."""
import asyncio
import uuid
from datetime import datetime, timezone

import structlog
from celery import current_app as celery_app  # noqa: F401 — available for send_task
from sqlalchemy import func, select, update  # noqa: F401
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import AsyncSessionLocal
from app.models.listing import Listing
from app.models.photo import Photo
from app.models.price_history import PriceHistory
from app.models.saved_search import PriceAlert
from app.models.source import Source
from app.models.user import User
from app.services import email_service
from app.tasks.celery_app import celery
from scraper.autodev import AutoDevPoller
from scraper.carmax import CarMaxPoller
from scraper.carvana import CarvanaPoller
from scraper.ebay import EBayMotorsPoller
from scraper.marketcheck import MarketCheckPoller
from scraper.normalizer import normalize

log = structlog.get_logger()

# Maps source name → Celery task name for the orchestrator
_TASK_MAP = {
    "autodev": "app.tasks.ingest.poll_autodev",
    "ebay": "app.tasks.ingest.poll_ebay",
    "carmax": "app.tasks.ingest.poll_carmax",
    "marketcheck": "app.tasks.ingest.poll_marketcheck",
    "carvana": "app.tasks.ingest.poll_carvana",
}


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _key_configured(source_name: str) -> bool:
    """Return True if the API key(s) required for this source are present."""
    from app.config import settings
    checks = {
        "autodev": bool(settings.autodev_api_key),
        "ebay": bool(settings.ebay_app_id and settings.ebay_cert_id),
        "marketcheck": bool(settings.marketcheck_api_key),
        "carvana": bool(settings.carvana_api_key),
        "carmax": True,
    }
    return checks.get(source_name, False)


async def _get_source_id(name: str) -> int | None:
    """Return the source's PK. Does NOT update last_polled (orchestrator owns that)."""
    async with AsyncSessionLocal() as db:
        row = await db.execute(select(Source).where(Source.name == name))
        source = row.scalar_one_or_none()
        if source:
            return source.id
        return None


async def _upsert_listings(source_name: str, raw_listings) -> int:
    """Upsert a list of raw listings into the DB. Returns the count upserted."""
    source_id = await _get_source_id(source_name)
    if source_id is None:
        log.warning("source_not_found", source=source_name)
        return 0

    async with AsyncSessionLocal() as db:
        for raw in raw_listings:
            norm = normalize(raw)
            listing_id = uuid.uuid4()

            stmt = (
                pg_insert(Listing)
                .values(
                    id=listing_id,
                    source_id=source_id,
                    external_id=norm["external_id"],
                    url=norm["url"],
                    title=norm["title"],
                    price=norm["price"],
                    mileage=norm["mileage"],
                    year=norm["year"],
                    make=norm["make"],
                    model=norm["model"],
                    trim=norm["trim"],
                    vin=None,  # populated later by the VIN decode task once vehicle record exists
                    condition=norm["condition"],
                    color_exterior=norm["color_exterior"],
                    color_interior=norm["color_interior"],
                    location_city=norm["location_city"],
                    location_state=norm["location_state"],
                    location_zip=norm["location_zip"],
                    dealer_name=norm["dealer_name"],
                    description=norm["description"],
                    source_raw=norm["source_raw"],
                    is_active=True,
                )
                .on_conflict_do_update(
                    constraint="uq_listing_source_external",
                    set_={
                        "price": norm["price"],
                        "mileage": norm["mileage"],
                        "is_active": True,
                        "last_seen_at": datetime.now(timezone.utc),
                        "source_raw": norm["source_raw"],
                    },
                )
                .returning(Listing.id, Listing.price)
            )
            result = await db.execute(stmt)
            row = result.fetchone()
            if row:
                returned_id, current_price = row
                # Record price history if price changed or first insert
                if norm["price"] is not None:
                    ph = PriceHistory(listing_id=returned_id, price=norm["price"])
                    db.add(ph)

                # Upsert photos (replace all on re-fetch)
                if norm["photo_urls"]:
                    await db.execute(
                        Photo.__table__.delete().where(Photo.listing_id == returned_id)
                    )
                    for i, url in enumerate(norm["photo_urls"]):
                        db.add(Photo(
                            listing_id=returned_id,
                            url=url,
                            is_primary=(i == 0),
                            sort_order=i,
                        ))

        await db.commit()
    log.info("upsert_complete", source=source_name, count=len(raw_listings))
    return len(raw_listings)


async def _update_source_stats(source_name: str, listings_count: int, error: str | None) -> None:
    """Increment poll counters and record error state for a source."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Source).where(Source.name == source_name))
        source = result.scalar_one_or_none()
        if source:
            source.total_polls += 1
            source.total_listings_ingested += listings_count
            if error:
                source.last_error = error
                source.last_error_at = datetime.now(timezone.utc)
            else:
                source.last_error = None
                source.last_error_at = None
            await db.commit()


@celery.task(name="app.tasks.ingest.poll_autodev", bind=True, max_retries=3)
def poll_autodev(self):
    try:
        listings = _run(AutoDevPoller().fetch())
        count = _run(_upsert_listings("autodev", listings))
        _run(_update_source_stats("autodev", count, None))
    except Exception as exc:
        log.error("poll_autodev_failed", error=str(exc))
        _run(_update_source_stats("autodev", 0, str(exc)))
        raise self.retry(exc=exc, countdown=60)


@celery.task(name="app.tasks.ingest.poll_ebay", bind=True, max_retries=3)
def poll_ebay(self):
    try:
        listings = _run(EBayMotorsPoller().fetch())
        count = _run(_upsert_listings("ebay", listings))
        _run(_update_source_stats("ebay", count, None))
    except Exception as exc:
        log.error("poll_ebay_failed", error=str(exc))
        _run(_update_source_stats("ebay", 0, str(exc)))
        raise self.retry(exc=exc, countdown=60)


@celery.task(name="app.tasks.ingest.poll_carmax", bind=True, max_retries=3)
def poll_carmax(self):
    try:
        listings = _run(CarMaxPoller().fetch())
        count = _run(_upsert_listings("carmax", listings))
        _run(_update_source_stats("carmax", count, None))
    except Exception as exc:
        log.error("poll_carmax_failed", error=str(exc))
        _run(_update_source_stats("carmax", 0, str(exc)))
        raise self.retry(exc=exc, countdown=60)


@celery.task(name="app.tasks.ingest.poll_marketcheck", bind=True, max_retries=3)
def poll_marketcheck(self):
    try:
        listings = _run(MarketCheckPoller().fetch())
        count = _run(_upsert_listings("marketcheck", listings))
        _run(_update_source_stats("marketcheck", count, None))
    except Exception as exc:
        log.error("poll_marketcheck_failed", error=str(exc))
        _run(_update_source_stats("marketcheck", 0, str(exc)))
        raise self.retry(exc=exc, countdown=60)


@celery.task(name="app.tasks.ingest.poll_carvana", bind=True, max_retries=3)
def poll_carvana(self):
    try:
        listings = _run(CarvanaPoller().fetch())
        count = _run(_upsert_listings("carvana", listings))
        _run(_update_source_stats("carvana", count, None))
    except Exception as exc:
        log.error("poll_carvana_failed", error=str(exc))
        _run(_update_source_stats("carvana", 0, str(exc)))
        raise self.retry(exc=exc, countdown=60)


@celery.task(name="app.tasks.ingest.orchestrator")
def orchestrator():
    """Check each enabled source and dispatch its poll task if the interval has elapsed."""
    async def _run_orch():
        now = datetime.now(timezone.utc)
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Source))
            sources = result.scalars().all()
            for source in sources:
                if not source.is_enabled or not source.is_active:
                    continue
                if not _key_configured(source.name):
                    continue
                interval_secs = (source.poll_interval_minutes or 60) * 60
                last = source.last_polled
                if last is None:
                    elapsed = interval_secs  # treat as overdue
                else:
                    aware_last = last if last.tzinfo is not None else last.replace(tzinfo=timezone.utc)
                    elapsed = (now - aware_last).total_seconds()
                if elapsed >= interval_secs:
                    source.last_polled = now  # mark dispatched to prevent double-dispatch
                    task_name = _TASK_MAP.get(source.name)
                    if task_name:
                        celery.send_task(task_name)
                        log.info("orchestrator_dispatched", source=source.name)
            await db.commit()
    _run(_run_orch())


@celery.task(name="app.tasks.ingest.check_price_alerts")
def check_price_alerts():
    async def _check():
        async with AsyncSessionLocal() as db:
            rows = await db.execute(
                select(PriceAlert, User.email, Listing.title, Listing.price, Listing.url)
                .join(Listing, PriceAlert.listing_id == Listing.id)
                .join(User, PriceAlert.user_id == User.id)
                .where(
                    PriceAlert.triggered == False,  # noqa: E712
                    Listing.price <= PriceAlert.target_price,
                    Listing.price != None,  # noqa: E711
                )
            )
            results = rows.all()
            for alert, user_email, listing_title, listing_price, listing_url in results:
                alert.triggered = True
                alert.triggered_at = datetime.now(timezone.utc)
                log.info("price_alert_triggered", alert_id=str(alert.id), email=user_email)
                try:
                    await email_service.send_price_alert_email(
                        to_email=user_email,
                        listing_title=listing_title or "Vehicle",
                        listing_url=listing_url,
                        target_price_cents=alert.target_price,
                        current_price_cents=listing_price,
                    )
                except Exception as e:
                    log.error("price_alert_email_failed", error=str(e), alert_id=str(alert.id))
            await db.commit()
    _run(_check())
