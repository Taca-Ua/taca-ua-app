"""Add name field to tiers

Revision ID: 003
Revises: 002
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, Sequence[str], None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add name field to tiers."""

    # Add the column with a server_default so existing rows get the value
    op.add_column(
        "modality_type_escaloes",
        sa.Column("name", sa.String(), nullable=True, server_default="Unnamed Tier"),
        schema="ranking",
    )

    # Alter the column to set NOT NULL and drop the server_default
    op.alter_column(
        "modality_type_escaloes",
        "name",
        nullable=False,
        server_default=None,
        schema="ranking",
    )


def downgrade() -> None:
    """Remove name field from tiers."""

    op.drop_column(
        "modality_type_escaloes",
        "name",
        schema="ranking",
    )
