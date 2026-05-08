from datetime import datetime

from sqlalchemy import DateTime, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    vin: Mapped[str] = mapped_column(String(17), primary_key=True)
    year: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    make: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trim: Mapped[str | None] = mapped_column(String(100), nullable=True)
    body_class: Mapped[str | None] = mapped_column(String(100), nullable=True)
    drive_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fuel_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    engine: Mapped[str | None] = mapped_column(String(100), nullable=True)
    doors: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    seats: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    nhtsa_raw: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    recall_count: Mapped[int] = mapped_column(SmallInteger, default=0)
    decoded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    listings: Mapped[list["Listing"]] = relationship(back_populates="vehicle")  # noqa: F821
