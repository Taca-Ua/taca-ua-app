"""seed seasons from modalities schema

Revision ID: 021
Revises: 020
Create Date: 2026-05-13

Migration to back-fill public_read.seasons and public_read.mv_season_details
from the modalities.season table, covering any seasons that were created
before the SeasonCreatedV1 event handler existed.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "021"
down_revision: Union[str, Sequence[str], None] = "020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed public_read.seasons and public_read.mv_season_details from modalities.season."""
    op.execute(
        """
        INSERT INTO public_read.seasons (season_id, name)
        SELECT id, name
        FROM modalities.season
        ON CONFLICT (season_id) DO UPDATE SET name = EXCLUDED.name;
        """
    )
    op.execute(
        """
        INSERT INTO public_read.mv_season_details (season_id, name)
        SELECT id, name
        FROM modalities.season
        ON CONFLICT (season_id) DO UPDATE SET name = EXCLUDED.name;
        """
    )


def downgrade() -> None:
    """Remove seeded data (leaves tables empty)."""
    op.execute("DELETE FROM public_read.mv_season_details;")
    op.execute("DELETE FROM public_read.seasons;")
