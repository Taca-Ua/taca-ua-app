"""Add competitor_type field to tournament

Revision ID: 007
Revises: 006
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, Sequence[str], None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add competitor_type field to tournament."""

    op.add_column(
        "tournament",
        sa.Column("competitor_type", sa.String(20), nullable=False),
        schema="tournaments",
    )


def downgrade() -> None:
    """Remove competitor_type field from tournament."""
    op.drop_column("tournament", "competitor_type", schema="tournaments")
