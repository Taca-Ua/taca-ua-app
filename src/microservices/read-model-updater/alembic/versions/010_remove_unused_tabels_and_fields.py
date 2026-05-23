"""
Remove unused tables and fields

Removes:
- Staff, TournamentRanking, MatchLineup tables (never used for view reconstruction)
- created_at from all core tables (not used in events or projections)
- updated_at from core tables and materialized views (metadata only, logs available)

Revision ID: 010
Revises: 009
Create Date: 2026-04-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: Union[str, Sequence[str], None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove unused tables and timestamp fields."""

    # Drop unused tables
    op.drop_table("staff", schema="public_read")
    op.drop_table("tournament_rankings", schema="public_read")
    op.drop_table("match_lineups", schema="public_read")

    # Remove created_at and updated_at from core tables
    op.drop_column("nucleos", "created_at", schema="public_read")
    op.drop_column("nucleos", "updated_at", schema="public_read")

    op.drop_column("courses", "created_at", schema="public_read")
    op.drop_column("courses", "updated_at", schema="public_read")

    op.drop_column("modality_types", "created_at", schema="public_read")
    op.drop_column("modality_types", "updated_at", schema="public_read")

    op.drop_column("modalities", "created_at", schema="public_read")
    op.drop_column("modalities", "updated_at", schema="public_read")

    op.drop_column("students", "created_at", schema="public_read")
    op.drop_column("students", "updated_at", schema="public_read")

    op.drop_column("teams", "created_at", schema="public_read")
    op.drop_column("teams", "updated_at", schema="public_read")

    op.drop_column("team_players", "added_at", schema="public_read")

    op.drop_column("tournaments", "created_at", schema="public_read")
    op.drop_column("tournaments", "updated_at", schema="public_read")

    op.drop_column("tournament_competitors", "added_at", schema="public_read")

    op.drop_column("matches", "created_at", schema="public_read")
    op.drop_column("matches", "updated_at", schema="public_read")

    op.drop_column("match_participants", "added_at", schema="public_read")

    op.drop_column("match_results", "updated_at", schema="public_read")

    op.drop_column("match_comments", "created_at", schema="public_read")

    # Remove updated_at from materialized views
    op.drop_column("mv_team_details", "updated_at", schema="public_read")
    op.drop_column("mv_student_details", "updated_at", schema="public_read")
    op.drop_column("mv_tournament_details", "updated_at", schema="public_read")
    op.drop_column("mv_match_details", "updated_at", schema="public_read")
    op.drop_column("mv_tournament_standings", "updated_at", schema="public_read")
    op.drop_column("mv_general_ranking", "updated_at", schema="public_read")
    op.drop_column("mv_modality_rankings", "updated_at", schema="public_read")


def downgrade() -> None:
    """Restore unused tables and timestamp fields."""

    # Restore updated_at to materialized views
    op.add_column(
        "mv_modality_rankings",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "mv_general_ranking",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "mv_tournament_standings",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "mv_match_details",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "mv_tournament_details",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "mv_student_details",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "mv_team_details",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore created_at to match_comments
    op.add_column(
        "match_comments",
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore updated_at to match_results
    op.add_column(
        "match_results",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore added_at to match_participants
    op.add_column(
        "match_participants",
        sa.Column(
            "added_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore created_at and updated_at to matches
    op.add_column(
        "matches",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "matches",
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore added_at to tournament_competitors
    op.add_column(
        "tournament_competitors",
        sa.Column(
            "added_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore created_at and updated_at to tournaments
    op.add_column(
        "tournaments",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "tournaments",
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore added_at to team_players
    op.add_column(
        "team_players",
        sa.Column(
            "added_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore created_at and updated_at to teams
    op.add_column(
        "teams",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "teams",
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore created_at and updated_at to students
    op.add_column(
        "students",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "students",
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore created_at and updated_at to modalities
    op.add_column(
        "modalities",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "modalities",
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore created_at and updated_at to modality_types
    op.add_column(
        "modality_types",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "modality_types",
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore created_at and updated_at to courses
    op.add_column(
        "courses",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "courses",
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore created_at and updated_at to nucleos
    op.add_column(
        "nucleos",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )
    op.add_column(
        "nucleos",
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        schema="public_read",
    )

    # Restore unused tables
    op.create_table(
        "match_lineups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("player_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("jersey_number", sa.Integer(), nullable=False),
        sa.Column("is_starter", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "assigned_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "team_id", "player_id", name="uq_match_lineup"),
        sa.Index("ix_match_lineups_match_id", "match_id"),
        sa.Index("ix_match_lineups_team_id", "team_id"),
        schema="public_read",
    )

    op.create_table(
        "tournament_rankings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tournament_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("competitor_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tournament_id", "competitor_id", name="uq_tournament_ranking"
        ),
        sa.Index("ix_tournament_rankings_tournament_id", "tournament_id"),
        sa.Index("ix_tournament_rankings_position", "tournament_id", "position"),
        schema="public_read",
    )

    op.create_table(
        "staff",
        sa.Column("staff_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("staff_number", sa.String(), nullable=False, unique=True),
        sa.Column("contact", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("staff_id"),
        sa.UniqueConstraint("staff_number", name="uq_staff_number"),
        schema="public_read",
    )
