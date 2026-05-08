import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.config import settings
from app.models.vehicle import Vehicle

log = structlog.get_logger()

_NHTSA_FIELD_MAP = {
    "Make": "make",
    "Model": "model",
    "ModelYear": "year",
    "BodyClass": "body_class",
    "DriveType": "drive_type",
    "FuelTypePrimary": "fuel_type",
    "EngineCylinders": "engine",
    "Seats": "seats",
    "Doors": "doors",
    "Trim": "trim",
}


def _parse_int(val: str | None) -> int | None:
    try:
        return int(val) if val else None
    except (ValueError, TypeError):
        return None


async def decode_vin(vin: str, db: AsyncSession) -> Vehicle | None:
    vin = vin.upper().strip()
    if len(vin) != 17:
        return None

    result = await db.execute(select(Vehicle).where(Vehicle.vin == vin))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"{settings.nhtsa_api_base}/vehicles/DecodeVinValuesExtended/{vin}?format=json"
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        raw = data.get("Results", [{}])[0]
        vehicle = Vehicle(
            vin=vin,
            make=raw.get("Make") or None,
            model=raw.get("Model") or None,
            year=_parse_int(raw.get("ModelYear")),
            trim=raw.get("Trim") or None,
            body_class=raw.get("BodyClass") or None,
            drive_type=raw.get("DriveType") or None,
            fuel_type=raw.get("FuelTypePrimary") or None,
            engine=raw.get("DisplacementL") or None,
            seats=_parse_int(raw.get("Seats")),
            doors=_parse_int(raw.get("Doors")),
            nhtsa_raw=raw,
            recall_count=await _get_recall_count(raw.get("Make"), raw.get("Model"), raw.get("ModelYear")),
        )
        db.add(vehicle)
        await db.flush()
        return vehicle

    except Exception as exc:
        log.warning("vin_decode_failed", vin=vin, error=str(exc))
        return None


async def _get_recall_count(make: str | None, model: str | None, year: str | None) -> int:
    if not all([make, model, year]):
        return 0
    try:
        url = f"{settings.nhtsa_recalls_base}/recallsByVehicle"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params={"make": make, "model": model, "modelYear": year})
            resp.raise_for_status()
            return resp.json().get("Count", 0)
    except Exception:
        return 0
