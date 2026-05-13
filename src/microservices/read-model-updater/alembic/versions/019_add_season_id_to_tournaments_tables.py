"""add season_id to tournaments tables

Revision ID: 019
Revises: 018
Create Date: 2026-05-13 02:16:55.757358

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "019"
down_revision: Union[str, Sequence[str], None] = "018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "tournaments",
        sa.Column("season_id", sa.Integer(), nullable=False, server_default="0"),
        schema="public_read",
    )
    op.add_column(
        "mv_tournament_details",
        sa.Column(
            "tournament_season_id", sa.Integer(), nullable=False, server_default="0"
        ),
        schema="public_read",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("tournaments", "season_id", schema="public_read")
    op.drop_column(
        "mv_tournament_details", "tournament_season_id", schema="public_read"
    )
