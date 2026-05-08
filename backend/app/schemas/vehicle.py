from datetime import datetime

from pydantic import BaseModel


class VehicleResponse(BaseModel):
    vin: str
    year: int | None
    make: str | None
    model: str | None
    trim: str | None
    body_class: str | None
    drive_type: str | None
    fuel_type: str | None
    engine: str | None
    doors: int | None
    seats: int | None
    recall_count: int
    decoded_at: datetime

    model_config = {"from_attributes": True}
