"""replace team with competitor entity

Revision ID: ebe27bde493d
Revises: aa1b2e5f58fb
Create Date: 2026-01-17 16:53:56.437565

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "ebe27bde493d"
down_revision: Union[str, Sequence[str], None] = "aa1b2e5f58fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create competitor_type enum
    # competitor_type_enum = sa.Enum('team', 'athlete', name='competitor_type', schema='tournaments')
    # competitor_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "tournament_competitor",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tournament_id", UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", UUID(as_uuid=True), nullable=True),
        sa.Column("athlete_id", UUID(as_uuid=True), nullable=True),
        sa.Column(
            "competitor_type",
            sa.Enum("TEAM", "ATHLETE", name="competitor_type", schema="tournaments"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["tournaments.tournament.id"], ondelete="CASCADE"
        ),
        schema="tournaments",
    )

    # Migrate data from tournament_teams to tournament_competitor
    connection = op.get_bind()
    results = connection.execute(
        sa.text("SELECT tournament_id, team_id FROM tournaments.tournament_teams")
    ).fetchall()
    for row in results:
        connection.execute(
            sa.text(
                """
                INSERT INTO tournaments.tournament_competitor (tournament_id, team_id, competitor_type)
                VALUES (:tournament_id, :team_id, 'team')
            """
            ),
            {"tournament_id": row["tournament_id"], "team_id": row["team_id"]},
        )

    # Drop old table
    op.drop_table("tournament_teams", schema="tournaments")


def downgrade() -> None:
    """Downgrade schema."""

    # Recreate tournament_teams table
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

    # Migrate data back from tournament_competitor to tournament_teams
    connection = op.get_bind()
    results = connection.execute(
        sa.text(
            """
            SELECT tournament_id, team_id FROM tournaments.tournament_competitor
            WHERE competitor_type = 'team'
        """
        )
    ).fetchall()
    for row in results:
        connection.execute(
            sa.text(
                """
                INSERT INTO tournaments.tournament_teams (tournament_id, team_id, created_at)
                VALUES (:tournament_id, :team_id, NOW())
            """
            ),
            {"tournament_id": row["tournament_id"], "team_id": row["team_id"]},
        )

    # Drop tournament_competitor table
    op.drop_table("tournament_competitor", schema="tournaments")

    # Drop competitor_type enum
    competitor_type_enum = sa.Enum(name="competitor_type", schema="tournaments")
    competitor_type_enum.drop(op.get_bind(), checkfirst=True)
