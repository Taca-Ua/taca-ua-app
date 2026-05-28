"""update mv tournament standings

Revision ID: 026
Revises: 025
Create Date: 2026-05-27 17:01:35.009880

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "026"
down_revision: Union[str, Sequence[str], None] = "025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "mv_tournament_standings",
        sa.Column("position", sa.Integer(), nullable=True),
        schema="public_read",
    )

    op.drop_index(
        "ix_mv_tournament_standings_rank",
        table_name="mv_tournament_standings",
        schema="public_read",
    )

    op.drop_column("mv_tournament_standings", "matches_played", schema="public_read")
    op.drop_column("mv_tournament_standings", "wins", schema="public_read")
    op.drop_column("mv_tournament_standings", "losses", schema="public_read")
    op.drop_column("mv_tournament_standings", "draws", schema="public_read")
    op.drop_column("mv_tournament_standings", "points", schema="public_read")
    op.drop_column("mv_tournament_standings", "total_score", schema="public_read")
    op.drop_column("mv_tournament_standings", "rank", schema="public_read")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "mv_tournament_standings",
        sa.Column("matches_played", sa.Integer(), nullable=False, server_default="0"),
        schema="public_read",
    )
    op.add_column(
        "mv_tournament_standings",
        sa.Column("wins", sa.Integer(), nullable=False, server_default="0"),
        schema="public_read",
    )
    op.add_column(
        "mv_tournament_standings",
        sa.Column("losses", sa.Integer(), nullable=False, server_default="0"),
        schema="public_read",
    )
    op.add_column(
        "mv_tournament_standings",
        sa.Column("draws", sa.Integer(), nullable=False, server_default="0"),
        schema="public_read",
    )
    op.add_column(
        "mv_tournament_standings",
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        schema="public_read",
    )
    op.add_column(
        "mv_tournament_standings",
        sa.Column("total_score", sa.Integer(), nullable=False, server_default="0"),
        schema="public_read",
    )
    op.add_column(
        "mv_tournament_standings",
        sa.Column("rank", sa.Integer(), nullable=True),
        schema="public_read",
    )
    op.create_index(
        "ix_mv_tournament_standings_rank",
        "mv_tournament_standings",
        ["rank"],
        schema="public_read",
    )
