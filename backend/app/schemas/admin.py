from datetime import datetime

from pydantic import BaseModel


class SourceStatus(BaseModel):
    id: int
    name: str
    base_url: str | None
    is_active: bool
    is_enabled: bool
    poll_interval_minutes: int
    last_polled: datetime | None
    total_polls: int
    total_listings_ingested: int
    last_error: str | None
    last_error_at: datetime | None
    api_key_configured: bool
    listing_count: int

    model_config = {"from_attributes": True}


class SourceUpdate(BaseModel):
    is_enabled: bool | None = None
    poll_interval_minutes: int | None = None


class AdminStats(BaseModel):
    total_listings: int
    active_listings: int
    total_users: int
    new_users_24h: int
    new_users_7d: int
    sources: list[SourceStatus]
    orchestrator_last_ran: datetime | None  # last time any source was polled


class UserSummary(BaseModel):
    id: str
    email: str
    is_active: bool
    is_verified: bool
    has_google: bool
    created_at: datetime
    saved_search_count: int

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    total: int
    users: list[UserSummary]
