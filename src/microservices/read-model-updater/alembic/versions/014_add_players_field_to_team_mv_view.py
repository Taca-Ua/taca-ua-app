"""add players field to team mv view

Revision ID: 014
Revises: 013
Create Date: 2026-04-27 15:25:29.577840

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "014"
down_revision: Union[str, Sequence[str], None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "mv_team_details",
        sa.Column("players", sa.JSON(), nullable=False, server_default="[]"),
        schema="public_read",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("mv_team_details", "players", schema="public_read")
