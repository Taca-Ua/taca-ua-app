"""add seasons tabels

Revision ID: 017
Revises: 016
Create Date: 2026-05-13 01:16:25.773090

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "017"
down_revision: Union[str, Sequence[str], None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "seasons",
        sa.Column("season_id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        schema="public_read",
    )
    op.create_table(
        "mv_season_details",
        sa.Column("season_id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        schema="public_read",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("mv_season_details", schema="public_read")
    op.drop_table("seasons", schema="public_read")
