"""add season_id to tournament

Revision ID: 06e506fcc9ce
Revises: 007
Create Date: 2026-05-02 01:41:11.646593

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "06e506fcc9ce"
down_revision: Union[str, Sequence[str], None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "tournament",
        sa.Column("season_id", sa.Integer(), nullable=True, index=True),
        schema="tournaments",
    )
    op.execute("UPDATE tournaments.tournament SET season_id = 0")
    op.alter_column(
        "tournament",
        "season_id",
        nullable=False,
        schema="tournaments",
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_tournament_season_id", table_name="tournament", schema="tournaments"
    )
    op.drop_column("tournament", "season_id", schema="tournaments")
    pass
