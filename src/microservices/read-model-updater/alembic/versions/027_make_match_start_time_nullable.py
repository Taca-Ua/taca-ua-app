"""make match start time nullable

Revision ID: 027
Revises: 026
Create Date: 2026-06-15 19:42:09.457835

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "027"
down_revision: Union[str, Sequence[str], None] = "026"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "matches",
        "start_time",
        existing_type=sa.DateTime(),
        nullable=True,
        schema="public_read",
    )
    op.alter_column(
        "mv_match_details",
        "start_time",
        existing_type=sa.DateTime(),
        nullable=True,
        schema="public_read",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "matches",
        "start_time",
        existing_type=sa.DateTime(),
        nullable=False,
        schema="public_read",
    )
    op.alter_column(
        "mv_match_details",
        "start_time",
        existing_type=sa.DateTime(),
        nullable=False,
        schema="public_read",
    )
