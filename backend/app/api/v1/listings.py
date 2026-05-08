import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.listing import Listing
from app.models.source import Source
from app.schemas.listing import ListingCard, ListingResponse, ListingSearchParams, PaginatedListings
from app.services import listing_service

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/featured", response_model=list[ListingCard])
async def featured(db: AsyncSession = Depends(get_db)):
    return await listing_service.get_featured(db)


@router.get("/stats")
async def public_stats(db: AsyncSession = Depends(get_db)):
    """Public endpoint: total listings, active listings, and source count."""
    total = (await db.execute(select(func.count()).select_from(Listing))).scalar_one()
    active = (
        await db.execute(
            select(func.count()).select_from(Listing).where(Listing.is_active == True)  # noqa: E712
        )
    ).scalar_one()
    sources = (
        await db.execute(
            select(func.count()).select_from(Source).where(Source.is_active == True)  # noqa: E712
        )
    ).scalar_one()
    return {"total_listings": total, "active_listings": active, "source_count": sources}


@router.get("", response_model=PaginatedListings)
async def search(
    make: str | None = Query(None),
    model: str | None = Query(None),
    year_min: int | None = Query(None),
    year_max: int | None = Query(None),
    price_min: int | None = Query(None),
    price_max: int | None = Query(None),
    mileage_max: int | None = Query(None),
    condition: str | None = Query(None),
    state: str | None = Query(None),
    query: str | None = Query(None),
    sort: str = Query("newest"),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    if price_min is not None and price_max is not None and price_min > price_max:
        raise HTTPException(status_code=422, detail="price_min must be ≤ price_max")
    if year_min is not None and year_max is not None and year_min > year_max:
        raise HTTPException(status_code=422, detail="year_min must be ≤ year_max")

    params = ListingSearchParams(
        make=make, model=model, year_min=year_min, year_max=year_max,
        price_min=price_min, price_max=price_max, mileage_max=mileage_max,
        condition=condition, state=state, query=query,
        sort=sort, page=page, page_size=page_size,
    )
    return await listing_service.search_listings(params, db)


@router.get("/{listing_id}", response_model=ListingResponse)
async def detail(listing_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    listing = await listing_service.get_listing_detail(listing_id, db)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing
