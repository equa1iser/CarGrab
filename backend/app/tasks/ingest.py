"""Celery tasks: poll sources, upsert listings, trigger price alerts."""
import asyncio
import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import AsyncSessionLocal
from app.models.listing import Listing
from app.models.photo import Photo
from app.models.price_history import PriceHistory
from app.models.saved_search import PriceAlert
from app.models.source import Source
from app.tasks.celery_app import celery
from scraper.carmax import CarMaxPoller
from scraper.carvana import CarvanaPoller
from scraper.marketcheck import MarketCheckPoller
from scraper.normalizer import normalize

log = structlog.get_logger()


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


async def _get_source_id(name: str) -> int | None:
    async with AsyncSessionLocal() as db:
        row = await db.execute(select(Source).where(Source.name == name))
        source = row.scalar_one_or_none()
        if source:
            source.last_polled = datetime.now(timezone.utc)
            return source.id
        return None


async def _upsert_listings(source_name: str, raw_listings) -> None:
    source_id = await _get_source_id(source_name)
    if source_id is None:
        log.warning("source_not_found", source=source_name)
        return

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
                    vin=norm["vin"],
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


@celery.task(name="app.tasks.ingest.poll_carmax", bind=True, max_retries=3)
def poll_carmax(self):
    try:
        listings = _run(CarMaxPoller().fetch())
        _run(_upsert_listings("carmax", listings))
    except Exception as exc:
        log.error("poll_carmax_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=60)


@celery.task(name="app.tasks.ingest.poll_marketcheck", bind=True, max_retries=3)
def poll_marketcheck(self):
    try:
        listings = _run(MarketCheckPoller().fetch())
        _run(_upsert_listings("marketcheck", listings))
    except Exception as exc:
        log.error("poll_marketcheck_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=60)


@celery.task(name="app.tasks.ingest.poll_carvana", bind=True, max_retries=3)
def poll_carvana(self):
    try:
        listings = _run(CarvanaPoller().fetch())
        _run(_upsert_listings("carvana", listings))
    except Exception as exc:
        log.error("poll_carvana_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=60)


@celery.task(name="app.tasks.ingest.check_price_alerts")
def check_price_alerts():
    async def _check():
        async with AsyncSessionLocal() as db:
            rows = await db.execute(
                select(PriceAlert)
                .join(Listing, PriceAlert.listing_id == Listing.id)
                .where(
                    PriceAlert.triggered == False,  # noqa: E712
                    Listing.price <= PriceAlert.target_price,
                )
            )
            alerts = rows.scalars().all()
            for alert in alerts:
                alert.triggered = True
                alert.triggered_at = datetime.now(timezone.utc)
                log.info("price_alert_triggered", alert_id=str(alert.id))
            await db.commit()
    _run(_check())
