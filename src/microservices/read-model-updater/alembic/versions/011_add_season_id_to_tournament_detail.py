"""Add season_id to mv_tournament_details

Revision ID: 011
Revises: 010
Create Date: 2025-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "mv_tournament_details",
        sa.Column("season_id", UUID(as_uuid=True), nullable=True),
        schema="public_read",
    )
    op.create_index(
        "ix_mv_tournament_details_season_id",
        "mv_tournament_details",
        ["season_id"],
        schema="public_read",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mv_tournament_details_season_id",
        table_name="mv_tournament_details",
        schema="public_read",
    )
    op.drop_column(
        "mv_tournament_details",
        "season_id",
        schema="public_read",
    )
