from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import current_user
from app.config import settings
from app.database import get_db
from app.models.listing import Listing
from app.models.saved_search import SavedSearch
from app.models.source import Source
from app.models.user import User
from app.schemas.admin import AdminStats, SourceStatus, SourceUpdate, UserListResponse, UserSummary
from app.services.auth_service import is_admin

router = APIRouter(prefix="/admin", tags=["admin"])


def _key_configured(name: str) -> bool:
    checks = {
        "autodev": bool(settings.autodev_api_key),
        "ebay": bool(settings.ebay_app_id and settings.ebay_cert_id),
        "marketcheck": bool(settings.marketcheck_api_key),
        "carvana": bool(settings.carvana_api_key),
        "carmax": True,
    }
    return checks.get(name, False)


async def require_admin(user: User = Depends(current_user)) -> User:
    if not is_admin(user.email):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/stats", response_model=AdminStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    now = datetime.now(timezone.utc)

    total_listings = (await db.execute(select(func.count()).select_from(Listing))).scalar_one()
    active_listings = (
        await db.execute(
            select(func.count()).select_from(Listing).where(Listing.is_active == True)  # noqa: E712
        )
    ).scalar_one()
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    new_24h = (
        await db.execute(
            select(func.count()).select_from(User).where(User.created_at >= now - timedelta(days=1))
        )
    ).scalar_one()
    new_7d = (
        await db.execute(
            select(func.count()).select_from(User).where(User.created_at >= now - timedelta(days=7))
        )
    ).scalar_one()

    sources_result = await db.execute(select(Source))
    sources = sources_result.scalars().all()

    # Build per-source listing counts in one query
    source_listing_counts: dict[int, int] = {}
    counts_result = await db.execute(
        select(Listing.source_id, func.count().label("cnt")).group_by(Listing.source_id)
    )
    for row in counts_result:
        source_listing_counts[row.source_id] = row.cnt

    source_statuses = []
    for s in sources:
        source_statuses.append(
            SourceStatus(
                id=s.id,
                name=s.name,
                base_url=s.base_url,
                is_active=s.is_active,
                is_enabled=s.is_enabled,
                poll_interval_minutes=s.poll_interval_minutes,
                last_polled=s.last_polled,
                total_polls=s.total_polls,
                total_listings_ingested=s.total_listings_ingested,
                last_error=s.last_error,
                last_error_at=s.last_error_at,
                api_key_configured=_key_configured(s.name),
                listing_count=source_listing_counts.get(s.id, 0),
            )
        )

    all_last_polled = [s.last_polled for s in sources if s.last_polled]
    orchestrator_last_ran = max(all_last_polled) if all_last_polled else None

    return AdminStats(
        total_listings=total_listings,
        active_listings=active_listings,
        total_users=total_users,
        new_users_24h=new_24h,
        new_users_7d=new_7d,
        sources=source_statuses,
        orchestrator_last_ran=orchestrator_last_ran,
    )


@router.patch("/sources/{source_id}", response_model=SourceStatus)
async def update_source(
    source_id: int,
    body: SourceUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    if body.is_enabled is not None:
        source.is_enabled = body.is_enabled
    if body.poll_interval_minutes is not None:
        if body.poll_interval_minutes < 1:
            raise HTTPException(status_code=422, detail="Interval must be at least 1 minute")
        source.poll_interval_minutes = body.poll_interval_minutes
    await db.commit()
    await db.refresh(source)
    cnt = (
        await db.execute(
            select(func.count()).select_from(Listing).where(Listing.source_id == source_id)
        )
    ).scalar_one()
    return SourceStatus(
        id=source.id,
        name=source.name,
        base_url=source.base_url,
        is_active=source.is_active,
        is_enabled=source.is_enabled,
        poll_interval_minutes=source.poll_interval_minutes,
        last_polled=source.last_polled,
        total_polls=source.total_polls,
        total_listings_ingested=source.total_listings_ingested,
        last_error=source.last_error,
        last_error_at=source.last_error_at,
        api_key_configured=_key_configured(source.name),
        listing_count=cnt,
    )


@router.post("/sources/{source_id}/trigger", status_code=202)
async def trigger_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    from app.tasks.ingest import _TASK_MAP
    task_name = _TASK_MAP.get(source.name)
    if not task_name:
        raise HTTPException(status_code=400, detail="No poll task for this source")
    from app.tasks.celery_app import celery
    celery.send_task(task_name)
    return {"queued": True, "source": source.name}


@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    total = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    offset = (page - 1) * page_size
    users_result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(offset).limit(page_size)
    )
    users = users_result.scalars().all()

    user_summaries = []
    for u in users:
        ss_count = (
            await db.execute(
                select(func.count()).select_from(SavedSearch).where(SavedSearch.user_id == u.id)
            )
        ).scalar_one()
        user_summaries.append(
            UserSummary(
                id=str(u.id),
                email=u.email,
                is_active=u.is_active,
                is_verified=u.is_verified,
                has_google=bool(u.google_id),
                created_at=u.created_at,
                saved_search_count=ss_count,
            )
        )
    return UserListResponse(total=total, users=user_summaries)
