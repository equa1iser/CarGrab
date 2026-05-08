from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.listing import Listing
from app.services import listing_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/suggestions")
async def suggestions(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    makes = await db.execute(
        select(distinct(Listing.make))
        .where(Listing.is_active == True, func.lower(Listing.make).contains(q.lower()))  # noqa: E712
        .limit(10)
    )
    models = await db.execute(
        select(distinct(Listing.model))
        .where(Listing.is_active == True, func.lower(Listing.model).contains(q.lower()))  # noqa: E712
        .limit(10)
    )
    return {
        "makes": [r[0] for r in makes if r[0]],
        "models": [r[0] for r in models if r[0]],
    }


@router.get("/facets")
async def facets(db: AsyncSession = Depends(get_db)):
    return await listing_service.get_search_facets(db)
