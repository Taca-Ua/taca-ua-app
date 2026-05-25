"""add seasons_id to regulations tabels

Revision ID: 020
Revises: 019
Create Date: 2026-05-13 02:28:30.631769

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "020"
down_revision: Union[str, Sequence[str], None] = "019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "regulation",
        sa.Column("season_id", sa.Integer(), nullable=False),
        schema="public_read",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("regulation", "season_id", schema="public_read")
