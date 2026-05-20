"""add league format tabels

Revision ID: 008
Revises: 06e506fcc9ce
Create Date: 2026-05-19 17:34:16.812674

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Union[str, Sequence[str], None] = "06e506fcc9ce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "tournament",
        sa.Column("format", sa.String(length=50), nullable=True),
        schema="tournaments",
    )
    op.execute(
        "UPDATE tournaments.tournament SET format = 'free'"
    )  # Set default format for existing records
    op.alter_column(
        "tournament",
        "format",
        existing_type=sa.String(length=50),
        nullable=False,
        schema="tournaments",
    )

    op.create_table(
        "league_tournaments",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("points_win", sa.Integer(), nullable=True),
        sa.Column("points_draw", sa.Integer(), nullable=True),
        sa.Column("points_loss", sa.Integer(), nullable=True),
        sa.Column("current_round", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"], ["tournaments.tournament.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="tournaments",
    )

    op.create_table(
        "league_standings",
        sa.Column("tournament_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("competitor_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("wins", sa.Integer(), nullable=True),
        sa.Column("losses", sa.Integer(), nullable=True),
        sa.Column("draws", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["tournaments.league_tournaments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["competitor_id"],
            ["tournaments.tournament_competitor.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("tournament_id", "competitor_id"),
        schema="tournaments",
    )

    op.create_table(
        "league_matches",
        sa.Column("tournament_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("match_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("results", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["tournaments.league_tournaments.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("tournament_id", "match_id"),
        schema="tournaments",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("league_matches", schema="tournaments")
    op.drop_table("league_standings", schema="tournaments")
    op.drop_table("league_tournaments", schema="tournaments")
    op.drop_column("tournament", "format", schema="tournaments")
