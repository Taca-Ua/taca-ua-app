"""add is_active to mv_season_details

Revision ID: 022
Revises: 021
Create Date: 2026-05-13

Add is_active column to public_read.mv_season_details and seed it
from modalities.season.finished_at IS NULL.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "022"
down_revision: Union[str, Sequence[str], None] = "021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "seasons",
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        schema="public_read",
    )
    op.add_column(
        "mv_season_details",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="false"),
        schema="public_read",
    )


def downgrade() -> None:
    op.drop_column("mv_season_details", "is_active", schema="public_read")
    op.drop_column("seasons", "finished_at", schema="public_read")
