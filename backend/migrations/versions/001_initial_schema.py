"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-08

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_pw", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # sources
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("base_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_polled", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # vehicles
    op.create_table(
        "vehicles",
        sa.Column("vin", sa.String(17), nullable=False),
        sa.Column("year", sa.SmallInteger(), nullable=True),
        sa.Column("make", sa.String(100), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("trim", sa.String(100), nullable=True),
        sa.Column("body_class", sa.String(100), nullable=True),
        sa.Column("drive_type", sa.String(50), nullable=True),
        sa.Column("fuel_type", sa.String(50), nullable=True),
        sa.Column("engine", sa.String(100), nullable=True),
        sa.Column("doors", sa.SmallInteger(), nullable=True),
        sa.Column("seats", sa.SmallInteger(), nullable=True),
        sa.Column("nhtsa_raw", postgresql.JSONB(), nullable=True),
        sa.Column("recall_count", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("decoded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("vin"),
    )

    # listings
    op.create_table(
        "listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("vin", sa.String(17), nullable=True),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("mileage", sa.Integer(), nullable=True),
        sa.Column("year", sa.SmallInteger(), nullable=True),
        sa.Column("make", sa.String(100), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("trim", sa.String(100), nullable=True),
        sa.Column("color_exterior", sa.String(100), nullable=True),
        sa.Column("color_interior", sa.String(100), nullable=True),
        sa.Column("condition", sa.String(50), nullable=True),
        sa.Column("location_city", sa.String(100), nullable=True),
        sa.Column("location_state", sa.String(2), nullable=True),
        sa.Column("location_zip", sa.String(10), nullable=True),
        sa.Column("lat", sa.Numeric(9, 6), nullable=True),
        sa.Column("lon", sa.Numeric(9, 6), nullable=True),
        sa.Column("dealer_name", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("source_raw", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["vin"], ["vehicles.vin"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_listing_source_external"),
    )
    op.create_index("ix_listing_make_model_year", "listings", ["make", "model", "year"])
    op.create_index("ix_listing_price", "listings", ["price"])
    op.create_index("ix_listing_mileage", "listings", ["mileage"])
    op.create_index("ix_listing_state", "listings", ["location_state"])
    op.create_index("ix_listing_is_active", "listings", ["is_active"])
    op.create_index("ix_listing_vin", "listings", ["vin"])
    op.execute(
        "CREATE INDEX ix_listing_fts ON listings USING GIN "
        "(to_tsvector('english', coalesce(title,'') || ' ' || coalesce(description,'')))"
    )

    # photos
    op.create_table(
        "photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("sort_order", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_photo_listing_id", "photos", ["listing_id"])

    # price_history
    op.create_table(
        "price_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_price_history_listing_id", "price_history", ["listing_id"])

    # saved_searches
    op.create_table(
        "saved_searches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("filters", postgresql.JSONB(), nullable=False),
        sa.Column("alert_email", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_saved_searches_user_id", "saved_searches", ["user_id"])

    # price_alerts
    op.create_table(
        "price_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_price", sa.Integer(), nullable=False),
        sa.Column("triggered", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_price_alerts_user_id", "price_alerts", ["user_id"])
    op.create_index("ix_price_alerts_listing_id", "price_alerts", ["listing_id"])

    # Seed default sources
    op.execute(
        "INSERT INTO sources (name, base_url, is_active) VALUES "
        "('carmax', 'https://www.carmax.com', true), "
        "('marketcheck', 'https://mc-api.marketcheck.com', true), "
        "('carvana', 'https://www.carvana.com', false)"
    )


def downgrade() -> None:
    op.drop_table("price_alerts")
    op.drop_table("saved_searches")
    op.drop_table("price_history")
    op.drop_table("photos")
    op.drop_table("listings")
    op.drop_table("vehicles")
    op.drop_table("sources")
    op.drop_table("users")
