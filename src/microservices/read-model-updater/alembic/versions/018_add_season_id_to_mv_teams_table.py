"""add season_id to mv_teams table

Revision ID: 018
Revises: 017
Create Date: 2026-05-13 01:56:34.260647

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "018"
down_revision: Union[str, Sequence[str], None] = "017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "teams",
        sa.Column("season_id", sa.Integer(), nullable=False, server_default="0"),
        schema="public_read",
    )
    op.add_column(
        "mv_team_details",
        sa.Column("team_season_id", sa.Integer(), nullable=False, server_default="0"),
        schema="public_read",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("mv_team_details", "team_season_id", schema="public_read")
    op.drop_column("teams", "season_id", schema="public_read")
