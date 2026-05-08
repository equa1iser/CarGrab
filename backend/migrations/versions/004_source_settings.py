"""add source settings and telemetry columns

Revision ID: 004
Revises: 003
Create Date: 2026-05-08
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns with server defaults so existing rows get values immediately
    op.add_column("sources", sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("sources", sa.Column("poll_interval_minutes", sa.Integer(), nullable=False, server_default="60"))
    op.add_column("sources", sa.Column("total_polls", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("sources", sa.Column("total_listings_ingested", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("sources", sa.Column("last_error", sa.Text(), nullable=True))
    op.add_column("sources", sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True))

    # Set per-source default poll intervals
    op.execute(
        "UPDATE sources SET poll_interval_minutes = 60  WHERE name = 'autodev'"
    )
    op.execute(
        "UPDATE sources SET poll_interval_minutes = 30  WHERE name = 'ebay'"
    )
    op.execute(
        "UPDATE sources SET poll_interval_minutes = 30  WHERE name = 'carmax'"
    )
    op.execute(
        "UPDATE sources SET poll_interval_minutes = 15  WHERE name = 'marketcheck'"
    )
    op.execute(
        "UPDATE sources SET poll_interval_minutes = 120 WHERE name = 'carvana'"
    )

    # Mirror is_active into is_enabled for existing rows
    op.execute(
        "UPDATE sources SET is_enabled = is_active"
    )


def downgrade() -> None:
    op.drop_column("sources", "last_error_at")
    op.drop_column("sources", "last_error")
    op.drop_column("sources", "total_listings_ingested")
    op.drop_column("sources", "total_polls")
    op.drop_column("sources", "poll_interval_minutes")
    op.drop_column("sources", "is_enabled")
