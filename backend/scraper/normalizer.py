"""Converts a RawListing into the kwargs dict needed to upsert a Listing row."""
from scraper.base import RawListing


def normalize(raw: RawListing) -> dict:
    photos = raw.photo_urls or []
    title = _build_title(raw)
    return {
        "external_id": raw.external_id,
        "url": raw.url,
        "title": title,
        "price": raw.price_cents,
        "mileage": raw.mileage,
        "year": raw.year,
        "make": raw.make,
        "model": raw.model,
        "trim": raw.trim,
        "vin": (raw.vin or "").strip().upper() or None,
        "condition": (raw.condition or "used").lower(),
        "color_exterior": raw.color_exterior,
        "color_interior": raw.color_interior,
        "location_city": raw.location_city,
        "location_state": (raw.location_state or "").upper() or None,
        "location_zip": raw.location_zip,
        "dealer_name": raw.dealer_name,
        "description": raw.description,
        "photo_urls": photos,
        "source_raw": raw.raw,
    }


def _build_title(raw: RawListing) -> str:
    parts = [str(raw.year) if raw.year else "", raw.make or "", raw.model or "", raw.trim or ""]
    return " ".join(p for p in parts if p).strip() or "Used Vehicle"
