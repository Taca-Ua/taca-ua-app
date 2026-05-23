"""add_tournament_teams_table

Revision ID: aa1b2e5f58fb
Revises: 824bb29c302e
Create Date: 2026-01-12 14:20:37.130573

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "aa1b2e5f58fb"
down_revision: Union[str, Sequence[str], None] = "824bb29c302e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create tournament_teams association table
    op.create_table(
        "tournament_teams",
        sa.Column("tournament_id", UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tournament_id"],
            ["tournaments.tournament.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("tournament_id", "team_id"),
        schema="tournaments",
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tournament_teams table
    op.drop_table("tournament_teams", schema="tournaments")
