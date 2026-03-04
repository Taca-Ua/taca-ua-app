"""TUA-160: Add tournament rankings table

Revision ID: b5d3f4e2a1c6
Revises: a3f8b2c1d9e4
Create Date: 2026-03-04 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b5d3f4e2a1c6"
down_revision: Union[str, Sequence[str], None] = "a3f8b2c1d9e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add tournament_rankings table to store final ranking entries
    from tournament.finished events.
    """

    # Create tournament_rankings table
    op.create_table(
        "tournament_rankings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tournament_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["public_read.tournaments.tournament_id"]
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tournament_id", "team_id", name="uq_tournament_ranking"),
        schema="public_read",
    )

    # Create indexes
    op.create_index(
        "ix_tournament_rankings_tournament_id",
        "tournament_rankings",
        ["tournament_id"],
        unique=False,
        schema="public_read",
    )

    op.create_index(
        "ix_tournament_rankings_position",
        "tournament_rankings",
        ["tournament_id", "position"],
        unique=False,
        schema="public_read",
    )


def downgrade() -> None:
    """
    Remove tournament_rankings table.
    """

    # Drop indexes
    op.drop_index(
        "ix_tournament_rankings_position",
        table_name="tournament_rankings",
        schema="public_read",
    )

    op.drop_index(
        "ix_tournament_rankings_tournament_id",
        table_name="tournament_rankings",
        schema="public_read",
    )

    # Drop table
    op.drop_table("tournament_rankings", schema="public_read")
