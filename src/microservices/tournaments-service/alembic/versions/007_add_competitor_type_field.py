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

    # Add the column as nullable with a temporary server_default so existing rows
    # receive a non-NULL value and the migration does not fail on non-empty tables.
    op.add_column(
        "tournament",
        sa.Column(
            "competitor_type",
            sa.String(20),
            nullable=True,
            server_default="",
        ),
        schema="tournaments",
    )

    # Now that all existing rows have a non-NULL value, enforce non-nullability
    # and drop the temporary default to match the intended final schema.
    op.alter_column(
        "tournament",
        "competitor_type",
        schema="tournaments",
        existing_type=sa.String(20),
        nullable=False,
        server_default=None,
    )
def downgrade() -> None:
    """Remove competitor_type field from tournament."""
    op.drop_column("tournament", "competitor_type", schema="tournaments")
