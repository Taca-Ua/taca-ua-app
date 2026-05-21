"""add tiebreker rule

Revision ID: 010
Revises: 009
Create Date: 2026-05-21 21:59:08.858168

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010"
down_revision: Union[str, Sequence[str], None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "league_tournaments",
        sa.Column(
            "points_diff_tiebreaker", sa.String(), nullable=False, server_default="none"
        ),
        schema="tournaments",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("league_tournaments", "points_diff_tiebreaker", schema="tournaments")
