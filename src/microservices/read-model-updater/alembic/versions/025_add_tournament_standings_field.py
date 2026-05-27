"""add tournament standings field

Revision ID: 025
Revises: 024
Create Date: 2026-05-27 16:06:06.181309

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "025"
down_revision: Union[str, Sequence[str], None] = "024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "tournaments",
        sa.Column(
            "format_type", sa.String(length=50), nullable=False, server_default="free"
        ),
        schema="public_read",
    )
    op.add_column(
        "tournaments",
        sa.Column("standings_metadata", sa.JSON(), nullable=True),
        schema="public_read",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("tournaments", "format_type", schema="public_read")
    op.drop_column("tournaments", "standings_metadata", schema="public_read")
