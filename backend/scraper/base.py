from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class RawListing:
    external_id: str
    url: str
    source_name: str
    price_cents: int | None = None
    mileage: int | None = None
    year: int | None = None
    make: str | None = None
    model: str | None = None
    trim: str | None = None
    vin: str | None = None
    condition: str | None = None
    color_exterior: str | None = None
    color_interior: str | None = None
    location_city: str | None = None
    location_state: str | None = None
    location_zip: str | None = None
    dealer_name: str | None = None
    description: str | None = None
    photo_urls: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


class BaseSource(ABC):
    name: str = ""

    @abstractmethod
    async def fetch(self) -> list[RawListing]:
        """Return all available listings from this source."""
        ...
