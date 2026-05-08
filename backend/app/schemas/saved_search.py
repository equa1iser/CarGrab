import uuid
from datetime import datetime

from pydantic import BaseModel


class SavedSearchCreate(BaseModel):
    name: str | None = None
    filters: dict
    alert_email: bool = False


class SavedSearchUpdate(BaseModel):
    alert_email: bool


class SavedSearchResponse(BaseModel):
    id: uuid.UUID
    name: str | None
    filters: dict
    alert_email: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PriceAlertCreate(BaseModel):
    listing_id: uuid.UUID
    target_price: int  # cents


class PriceAlertResponse(BaseModel):
    id: uuid.UUID
    listing_id: uuid.UUID
    target_price: int
    triggered: bool
    triggered_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
