import math
import uuid

import structlog
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.listing import Listing
from app.models.photo import Photo
from app.models.source import Source
from app.schemas.listing import ListingCard, ListingResponse, ListingSearchParams, PaginatedListings

log = structlog.get_logger()

_SORT_MAP = {
    "newest": Listing.first_seen_at.desc(),
    "price_asc": Listing.price.asc(),
    "price_desc": Listing.price.desc(),
    "mileage_asc": Listing.mileage.asc(),
}


def _build_query(params: ListingSearchParams):
    q = select(Listing).where(Listing.is_active == True)  # noqa: E712

    if params.make:
        q = q.where(func.lower(Listing.make) == params.make.lower())
    if params.model:
        q = q.where(func.lower(Listing.model).contains(params.model.lower()))
    if params.year_min:
        q = q.where(Listing.year >= params.year_min)
    if params.year_max:
        q = q.where(Listing.year <= params.year_max)
    if params.price_min is not None:
        q = q.where(Listing.price >= params.price_min)
    if params.price_max is not None:
        q = q.where(Listing.price <= params.price_max)
    if params.mileage_max is not None:
        q = q.where(Listing.mileage <= params.mileage_max)
    if params.condition:
        q = q.where(func.lower(Listing.condition) == params.condition.lower())
    if params.state:
        q = q.where(Listing.location_state == params.state.upper())
    if params.query:
        q = q.where(
            text("to_tsvector('english', coalesce(listings.title,'') || ' ' || coalesce(listings.description,'')) @@ plainto_tsquery('english', :q)")
            .bindparams(q=params.query)
        )

    return q


def _primary_photo(listing: Listing) -> str | None:
    for p in listing.photos:
        if p.is_primary:
            return p.url
    return listing.photos[0].url if listing.photos else None


def _to_card(listing: Listing) -> ListingCard:
    return ListingCard(
        id=listing.id,
        url=listing.url,
        title=listing.title,
        price=listing.price,
        mileage=listing.mileage,
        year=listing.year,
        make=listing.make,
        model=listing.model,
        trim=listing.trim,
        condition=listing.condition,
        location_city=listing.location_city,
        location_state=listing.location_state,
        dealer_name=listing.dealer_name,
        source_name=listing.source.name if listing.source else None,
        primary_photo_url=_primary_photo(listing),
        first_seen_at=listing.first_seen_at,
    )


async def search_listings(params: ListingSearchParams, db: AsyncSession) -> PaginatedListings:
    base_q = _build_query(params)

    count_result = await db.execute(select(func.count()).select_from(base_q.subquery()))
    total = count_result.scalar_one()

    sort_col = _SORT_MAP.get(params.sort, Listing.first_seen_at.desc())
    offset = (params.page - 1) * params.page_size

    rows = await db.execute(
        base_q.options(
            selectinload(Listing.photos),
            selectinload(Listing.source),
        )
        .order_by(sort_col)
        .offset(offset)
        .limit(params.page_size)
    )
    listings = rows.scalars().all()

    return PaginatedListings(
        items=[_to_card(l) for l in listings],
        total=total,
        page=params.page,
        page_size=params.page_size,
        pages=math.ceil(total / params.page_size) if total else 0,
    )


async def get_featured(db: AsyncSession, limit: int = 8) -> list[ListingCard]:
    rows = await db.execute(
        select(Listing)
        .where(Listing.is_active == True)  # noqa: E712
        .options(selectinload(Listing.photos), selectinload(Listing.source))
        .order_by(Listing.first_seen_at.desc())
        .limit(limit)
    )
    return [_to_card(l) for l in rows.scalars().all()]


async def get_listing_detail(listing_id: uuid.UUID, db: AsyncSession) -> ListingResponse | None:
    row = await db.execute(
        select(Listing)
        .where(Listing.id == listing_id, Listing.is_active == True)  # noqa: E712
        .options(
            selectinload(Listing.photos),
            selectinload(Listing.source),
            selectinload(Listing.vehicle),
            selectinload(Listing.price_history),
        )
    )
    listing = row.scalar_one_or_none()
    if not listing:
        return None

    from app.schemas.vehicle import VehicleResponse
    from app.schemas.listing import PhotoOut, PriceHistoryPoint

    return ListingResponse(
        id=listing.id,
        url=listing.url,
        title=listing.title,
        price=listing.price,
        mileage=listing.mileage,
        year=listing.year,
        make=listing.make,
        model=listing.model,
        trim=listing.trim,
        condition=listing.condition,
        location_city=listing.location_city,
        location_state=listing.location_state,
        location_zip=listing.location_zip,
        dealer_name=listing.dealer_name,
        description=listing.description,
        color_exterior=listing.color_exterior,
        color_interior=listing.color_interior,
        vin=listing.vin,
        source_name=listing.source.name if listing.source else None,
        primary_photo_url=_primary_photo(listing),
        first_seen_at=listing.first_seen_at,
        last_seen_at=listing.last_seen_at,
        photos=[PhotoOut.model_validate(p) for p in listing.photos],
        price_history=[PriceHistoryPoint.model_validate(ph) for ph in listing.price_history],
        vehicle=VehicleResponse.model_validate(listing.vehicle) if listing.vehicle else None,
    )


async def get_similar_listings(listing: Listing, db: AsyncSession, limit: int = 4) -> list[ListingCard]:
    if not listing.make or not listing.model:
        return []
    rows = await db.execute(
        select(Listing)
        .where(
            Listing.is_active == True,  # noqa: E712
            Listing.id != listing.id,
            func.lower(Listing.make) == (listing.make or "").lower(),
            func.lower(Listing.model) == (listing.model or "").lower(),
        )
        .options(selectinload(Listing.photos), selectinload(Listing.source))
        .order_by(func.abs(Listing.price - (listing.price or 0)))
        .limit(limit)
    )
    return [_to_card(l) for l in rows.scalars().all()]


async def get_search_facets(db: AsyncSession) -> dict:
    makes = await db.execute(
        select(Listing.make, func.count(Listing.id))
        .where(Listing.is_active == True, Listing.make != None)  # noqa: E711, E712
        .group_by(Listing.make)
        .order_by(func.count(Listing.id).desc())
        .limit(30)
    )
    states = await db.execute(
        select(Listing.location_state, func.count(Listing.id))
        .where(Listing.is_active == True, Listing.location_state != None)  # noqa: E711, E712
        .group_by(Listing.location_state)
        .order_by(func.count(Listing.id).desc())
    )
    conditions = await db.execute(
        select(Listing.condition, func.count(Listing.id))
        .where(Listing.is_active == True, Listing.condition != None)  # noqa: E711, E712
        .group_by(Listing.condition)
    )
    return {
        "makes": [{"value": r[0], "count": r[1]} for r in makes],
        "states": [{"value": r[0], "count": r[1]} for r in states],
        "conditions": [{"value": r[0], "count": r[1]} for r in conditions],
    }
