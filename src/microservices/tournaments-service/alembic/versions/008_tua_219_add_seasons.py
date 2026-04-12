"""TUA-219: Add seasons table and season_id FK to tournaments

Revision ID: 008
Revises: 007
Create Date: 2026-04-12 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "008"
down_revision: Union[str, Sequence[str], None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the seasons table
    op.create_table(
        "season",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        schema="tournaments",
    )

    op.create_index(
        "ix_tournaments_season_status",
        "season",
        ["status"],
        schema="tournaments",
    )

    # Add season_id FK to tournaments
    op.add_column(
        "tournament",
        sa.Column("season_id", UUID(as_uuid=True), nullable=True),
        schema="tournaments",
    )

    op.create_foreign_key(
        "fk_tournament_season_id",
        "tournament",
        "season",
        ["season_id"],
        ["id"],
        source_schema="tournaments",
        referent_schema="tournaments",
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_tournaments_tournament_season_id",
        "tournament",
        ["season_id"],
        schema="tournaments",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_tournaments_tournament_season_id",
        table_name="tournament",
        schema="tournaments",
    )
    op.drop_constraint(
        "fk_tournament_season_id",
        "tournament",
        schema="tournaments",
        type_="foreignkey",
    )
    op.drop_column("tournament", "season_id", schema="tournaments")

    op.drop_index(
        "ix_tournaments_season_status",
        table_name="season",
        schema="tournaments",
    )
    op.drop_table("season", schema="tournaments")
