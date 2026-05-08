import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Listing(Base):
    __tablename__ = "listings"
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_listing_source_external"),
        Index("ix_listing_make_model_year", "make", "model", "year"),
        Index("ix_listing_price", "price"),
        Index("ix_listing_mileage", "mileage"),
        Index("ix_listing_state", "location_state"),
        Index("ix_listing_is_active", "is_active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vin: Mapped[str | None] = mapped_column(ForeignKey("vehicles.vin"), nullable=True, index=True)

    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Stored in cents to avoid float precision issues (e.g. $24,500 = 2450000)
    price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mileage: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Denormalized for fast filtering without joining vehicles
    year: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    make: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trim: Mapped[str | None] = mapped_column(String(100), nullable=True)

    color_exterior: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color_interior: Mapped[str | None] = mapped_column(String(100), nullable=True)
    condition: Mapped[str | None] = mapped_column(String(50), nullable=True)

    location_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location_state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    location_zip: Mapped[str | None] = mapped_column(String(10), nullable=True)
    lat: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    lon: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)

    dealer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    source_raw: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    source: Mapped["Source"] = relationship(back_populates="listings")  # noqa: F821
    vehicle: Mapped["Vehicle | None"] = relationship(back_populates="listings")  # noqa: F821
    photos: Mapped[list["Photo"]] = relationship(back_populates="listing", cascade="all, delete-orphan", order_by="Photo.sort_order")  # noqa: F821
    price_history: Mapped[list["PriceHistory"]] = relationship(back_populates="listing", cascade="all, delete-orphan")  # noqa: F821
    price_alerts: Mapped[list["PriceAlert"]] = relationship(back_populates="listing", cascade="all, delete-orphan")  # noqa: F821
