import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import current_user
from app.database import get_db
from app.models.saved_search import PriceAlert, SavedSearch
from app.models.user import User
from app.schemas.saved_search import (
    PriceAlertCreate,
    PriceAlertResponse,
    SavedSearchCreate,
    SavedSearchResponse,
)

router = APIRouter(tags=["saved"])


# ── Saved searches ─────────────────────────────────────────────────────────────

@router.get("/saved-searches", response_model=list[SavedSearchResponse])
async def list_saved_searches(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(select(SavedSearch).where(SavedSearch.user_id == user.id))
    return [SavedSearchResponse.model_validate(r) for r in rows.scalars().all()]


@router.post("/saved-searches", response_model=SavedSearchResponse, status_code=status.HTTP_201_CREATED)
async def create_saved_search(
    body: SavedSearchCreate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    ss = SavedSearch(user_id=user.id, **body.model_dump())
    db.add(ss)
    await db.flush()
    return SavedSearchResponse.model_validate(ss)


@router.delete("/saved-searches/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_search(
    search_id: uuid.UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(
        select(SavedSearch).where(SavedSearch.id == search_id, SavedSearch.user_id == user.id)
    )
    ss = row.scalar_one_or_none()
    if not ss:
        raise HTTPException(status_code=404, detail="Saved search not found")
    await db.delete(ss)


# ── Price alerts ───────────────────────────────────────────────────────────────

@router.get("/alerts", response_model=list[PriceAlertResponse])
async def list_alerts(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(select(PriceAlert).where(PriceAlert.user_id == user.id))
    return [PriceAlertResponse.model_validate(r) for r in rows.scalars().all()]


@router.post("/alerts", response_model=PriceAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    body: PriceAlertCreate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    alert = PriceAlert(user_id=user.id, **body.model_dump())
    db.add(alert)
    await db.flush()
    return PriceAlertResponse.model_validate(alert)


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: uuid.UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(
        select(PriceAlert).where(PriceAlert.id == alert_id, PriceAlert.user_id == user.id)
    )
    alert = row.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    await db.delete(alert)
