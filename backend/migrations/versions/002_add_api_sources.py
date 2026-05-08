"""add autodev and ebay sources

Revision ID: 002
Revises: 001
Create Date: 2026-05-08
"""
from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "INSERT INTO sources (name, base_url, is_active) VALUES "
        "('autodev', 'https://auto.dev/api', true), "
        "('ebay', 'https://api.ebay.com', true) "
        "ON CONFLICT (name) DO NOTHING"
    )


def downgrade() -> None:
    op.execute("DELETE FROM sources WHERE name IN ('autodev', 'ebay')")
