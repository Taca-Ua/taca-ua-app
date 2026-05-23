"""add nucleos detail view table

Revision ID: 013
Revises: 012
Create Date: 2026-04-27 14:18:47.896132

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "013"
down_revision: Union[str, Sequence[str], None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "mv_nucleo_details",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nucleo_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("abbreviation", sa.String(), nullable=False),
        sa.Column("logo_url", sa.String(), nullable=True),
        schema="public_read",
    )
    op.create_index(
        "ix_mv_nucleo_details_nucleo_id",
        "mv_nucleo_details",
        ["id"],
        unique=True,
        schema="public_read",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_mv_nucleo_details_nucleo_id",
        table_name="mv_nucleo_details",
        schema="public_read",
    )
    op.drop_table("mv_nucleo_details", schema="public_read")
