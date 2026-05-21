"""add journy to mathes

Revision ID: 004
Revises: 003
Create Date: 2026-05-16 18:31:50.123091

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, Sequence[str], None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "match",
        sa.Column("journey", sa.Integer(), nullable=False, server_default=sa.text("1")),
        schema="matches",
    )
    op.alter_column(
        "match", "journey", server_default=None, schema="matches"
    )  # Remove default after setting initial value


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("match", "journey", schema="matches")
