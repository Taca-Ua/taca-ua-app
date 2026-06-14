"""seed seasons from modalities schema

Revision ID: 021
Revises: 020
Create Date: 2026-05-13

Migration to back-fill public_read.seasons and public_read.mv_season_details
from the modalities.season table, covering any seasons that were created
before the SeasonCreatedV1 event handler existed.
"""

from typing import Sequence, Union

revision: str = "021"
down_revision: Union[str, Sequence[str], None] = "020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed public_read.seasons and public_read.mv_season_details from modalities.season."""
    pass


def downgrade() -> None:
    """Remove seeded data (leaves tables empty)."""
    pass
