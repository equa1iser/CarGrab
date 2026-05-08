import uuid
from datetime import datetime

from pydantic import BaseModel, computed_field

from app.schemas.vehicle import VehicleResponse


def cents_to_dollars(cents: int | None) -> str:
    if cents is None:
        return "N/A"
    return f"${cents / 100:,.0f}"


class ListingSearchParams(BaseModel):
    make: str | None = None
    model: str | None = None
    year_min: int | None = None
    year_max: int | None = None
    price_min: int | None = None   # cents
    price_max: int | None = None   # cents
    mileage_max: int | None = None
    condition: str | None = None
    state: str | None = None
    query: str | None = None       # full-text search
    sort: str = "newest"           # newest | price_asc | price_desc | mileage_asc
    page: int = 1
    page_size: int = 24


class PhotoOut(BaseModel):
    id: uuid.UUID
    url: str
    is_primary: bool
    sort_order: int

    model_config = {"from_attributes": True}


class PriceHistoryPoint(BaseModel):
    price: int
    recorded_at: datetime

    @computed_field
    @property
    def price_formatted(self) -> str:
        return cents_to_dollars(self.price)

    model_config = {"from_attributes": True}


class ListingCard(BaseModel):
    id: uuid.UUID
    url: str
    title: str | None
    price: int | None
    mileage: int | None
    year: int | None
    make: str | None
    model: str | None
    trim: str | None
    condition: str | None
    location_city: str | None
    location_state: str | None
    dealer_name: str | None
    source_name: str | None = None
    primary_photo_url: str | None = None
    first_seen_at: datetime

    @computed_field
    @property
    def price_formatted(self) -> str:
        return cents_to_dollars(self.price)

    model_config = {"from_attributes": True}


class ListingResponse(ListingCard):
    description: str | None
    color_exterior: str | None
    color_interior: str | None
    location_zip: str | None
    vin: str | None
    photos: list[PhotoOut] = []
    price_history: list[PriceHistoryPoint] = []
    vehicle: VehicleResponse | None = None
    last_seen_at: datetime


class PaginatedListings(BaseModel):
    items: list[ListingCard]
    total: int
    page: int
    page_size: int
    pages: int
