"""TUA-142: Fix comprehensive read models schema

Revision ID: a3f8b2c1d9e4
Revises: 4e8c9a5b7f2d
Create Date: 2026-02-15 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a3f8b2c1d9e4"
down_revision: Union[str, Sequence[str], None] = "4e8c9a5b7f2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema by dropping old tables and creating correct ones.
    Data is ephemeral and will be reconstructed from events.
    """

    # Drop old tables in reverse dependency order
    op.drop_table("match_comments", schema="public_read")
    op.drop_table("match_lineups", schema="public_read")
    op.drop_table("match_results", schema="public_read")
    op.drop_table("match_participants", schema="public_read")
    op.drop_table("matches", schema="public_read")
    op.drop_table("tournament_competitors", schema="public_read")
    op.drop_table("tournaments", schema="public_read")
    op.drop_table("team_players", schema="public_read")
    op.drop_table("teams", schema="public_read")
    op.drop_table("staff", schema="public_read")
    op.drop_table("students", schema="public_read")
    op.drop_table("modalities", schema="public_read")
    op.drop_table("modality_types", schema="public_read")
    op.drop_table("courses", schema="public_read")
    op.drop_table("nucleos", schema="public_read")

    # Drop old views
    op.drop_table("ranking_view", schema="public_read")
    op.drop_table("tournament_view", schema="public_read")
    op.drop_table("games_view", schema="public_read")

    # ==================== Create Core Read Models ====================

    # Create nucleos table with correct schema
    op.create_table(
        "nucleos",
        sa.Column("nucleo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("abbreviation", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("nucleo_id"),
        schema="public_read",
    )

    # Create courses table
    op.create_table(
        "courses",
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nucleo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("abbreviation", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["nucleo_id"], ["public_read.nucleos.nucleo_id"]),
        sa.PrimaryKeyConstraint("course_id"),
        schema="public_read",
    )

    # Create modality_types table
    op.create_table(
        "modality_types",
        sa.Column("modality_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("escaloes", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("modality_type_id"),
        schema="public_read",
    )

    # Create modalities table
    op.create_table(
        "modalities",
        sa.Column("modality_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["modality_type_id"], ["public_read.modality_types.modality_type_id"]
        ),
        sa.PrimaryKeyConstraint("modality_id"),
        schema="public_read",
    )

    # Create students table
    op.create_table(
        "students",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_number", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("is_member", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["course_id"], ["public_read.courses.course_id"]),
        sa.PrimaryKeyConstraint("student_id"),
        sa.UniqueConstraint("student_number", name="uq_student_number"),
        schema="public_read",
    )

    # Create staff table
    op.create_table(
        "staff",
        sa.Column("staff_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("staff_number", sa.String(), nullable=False),
        sa.Column("contact", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("staff_id"),
        sa.UniqueConstraint("staff_number", name="uq_staff_number"),
        schema="public_read",
    )

    # Create teams table
    op.create_table(
        "teams",
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["course_id"], ["public_read.courses.course_id"]),
        sa.ForeignKeyConstraint(
            ["modality_id"], ["public_read.modalities.modality_id"]
        ),
        sa.PrimaryKeyConstraint("team_id"),
        schema="public_read",
    )

    # Create team_players table
    op.create_table(
        "team_players",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("removed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["public_read.students.student_id"]),
        sa.ForeignKeyConstraint(["team_id"], ["public_read.teams.team_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("team_id", "student_id", name="uq_team_student"),
        schema="public_read",
    )
    op.create_index(
        "ix_team_players_team_id", "team_players", ["team_id"], schema="public_read"
    )
    op.create_index(
        "ix_team_players_student_id",
        "team_players",
        ["student_id"],
        schema="public_read",
    )

    # Create tournaments table
    op.create_table(
        "tournaments",
        sa.Column("tournament_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["modality_id"], ["public_read.modalities.modality_id"]
        ),
        sa.PrimaryKeyConstraint("tournament_id"),
        schema="public_read",
    )

    # Create tournament_competitors table
    op.create_table(
        "tournament_competitors",
        sa.Column("competitor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tournament_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "competitor_type",
            sa.Enum("TEAM", "ATHLETE", name="participanttype"),
            nullable=False,
        ),
        sa.Column(
            "competitor_entity_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["public_read.tournaments.tournament_id"]
        ),
        sa.PrimaryKeyConstraint("competitor_id"),
        sa.UniqueConstraint(
            "tournament_id", "competitor_entity_id", name="uq_tournament_competitor"
        ),
        schema="public_read",
    )
    op.create_index(
        "ix_tournament_competitors_tournament_id",
        "tournament_competitors",
        ["tournament_id"],
        schema="public_read",
    )
    op.create_index(
        "ix_tournament_competitors_entity_id",
        "tournament_competitors",
        ["competitor_entity_id"],
        schema="public_read",
    )

    # Create matches table
    op.create_table(
        "matches",
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tournament_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "SCHEDULED",
                "IN_PROGRESS",
                "COMPLETED",
                "FINISHED",
                "CANCELLED",
                name="matchstatus",
            ),
            nullable=False,
        ),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["public_read.tournaments.tournament_id"]
        ),
        sa.PrimaryKeyConstraint("match_id"),
        schema="public_read",
    )
    op.create_index(
        "ix_matches_tournament_id", "matches", ["tournament_id"], schema="public_read"
    )
    op.create_index("ix_matches_status", "matches", ["status"], schema="public_read")
    op.create_index(
        "ix_matches_start_time", "matches", ["start_time"], schema="public_read"
    )

    # Create match_participants table
    op.create_table(
        "match_participants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("participant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "participant_type",
            sa.Enum("TEAM", "ATHLETE", name="participanttype"),
            nullable=False,
        ),
        sa.Column(
            "participant_entity_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("removed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["public_read.matches.match_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "participant_id", name="uq_match_participant"),
        sa.UniqueConstraint("participant_id"),
        schema="public_read",
    )
    op.create_index(
        "ix_match_participants_match_id",
        "match_participants",
        ["match_id"],
        schema="public_read",
    )
    op.create_index(
        "ix_match_participants_entity_id",
        "match_participants",
        ["participant_entity_id"],
        schema="public_read",
    )

    # Create match_results table
    op.create_table(
        "match_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("participant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column(
            "results_metadata", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["public_read.matches.match_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "participant_id", name="uq_match_result"),
        schema="public_read",
    )
    op.create_index(
        "ix_match_results_match_id", "match_results", ["match_id"], schema="public_read"
    )
    op.create_index(
        "ix_match_results_participant_id",
        "match_results",
        ["participant_id"],
        schema="public_read",
    )

    # Create match_lineups table
    op.create_table(
        "match_lineups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("jersey_number", sa.Integer(), nullable=False),
        sa.Column("is_starter", sa.Boolean(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["public_read.matches.match_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "team_id", "player_id", name="uq_match_lineup"),
        schema="public_read",
    )
    op.create_index(
        "ix_match_lineups_match_id", "match_lineups", ["match_id"], schema="public_read"
    )
    op.create_index(
        "ix_match_lineups_team_id", "match_lineups", ["team_id"], schema="public_read"
    )

    # Create match_comments table
    op.create_table(
        "match_comments",
        sa.Column("comment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["public_read.matches.match_id"]),
        sa.PrimaryKeyConstraint("comment_id"),
        schema="public_read",
    )
    op.create_index(
        "ix_match_comments_match_id",
        "match_comments",
        ["match_id"],
        schema="public_read",
    )

    # ==================== Create Materialized Views ====================

    # Create mv_team_details
    op.create_table(
        "mv_team_details",
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("team_name", sa.String(), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("course_name", sa.String(), nullable=False),
        sa.Column("course_abbreviation", sa.String(), nullable=False),
        sa.Column("nucleo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nucleo_name", sa.String(), nullable=False),
        sa.Column("nucleo_abbreviation", sa.String(), nullable=False),
        sa.Column("modality_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_name", sa.String(), nullable=True),
        sa.Column("modality_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_type_name", sa.String(), nullable=False),
        sa.Column("player_count", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("team_id"),
        schema="public_read",
    )
    op.create_index(
        "ix_mv_team_details_course_id",
        "mv_team_details",
        ["course_id"],
        schema="public_read",
    )
    op.create_index(
        "ix_mv_team_details_modality_id",
        "mv_team_details",
        ["modality_id"],
        schema="public_read",
    )

    # Create mv_student_details
    op.create_table(
        "mv_student_details",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_number", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("is_member", sa.Boolean(), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("course_name", sa.String(), nullable=False),
        sa.Column("course_abbreviation", sa.String(), nullable=False),
        sa.Column("nucleo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nucleo_name", sa.String(), nullable=False),
        sa.Column("nucleo_abbreviation", sa.String(), nullable=False),
        sa.Column("team_count", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("student_id"),
        schema="public_read",
    )
    op.create_index(
        "ix_mv_student_details_course_id",
        "mv_student_details",
        ["course_id"],
        schema="public_read",
    )
    op.create_index(
        "ix_mv_student_details_student_number",
        "mv_student_details",
        ["student_number"],
        schema="public_read",
    )

    # Create mv_tournament_details
    op.create_table(
        "mv_tournament_details",
        sa.Column("tournament_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tournament_name", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("modality_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_name", sa.String(), nullable=True),
        sa.Column("modality_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_type_name", sa.String(), nullable=False),
        sa.Column("competitor_count", sa.Integer(), nullable=False),
        sa.Column("match_count", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("tournament_id"),
        schema="public_read",
    )
    op.create_index(
        "ix_mv_tournament_details_modality_id",
        "mv_tournament_details",
        ["modality_id"],
        schema="public_read",
    )
    op.create_index(
        "ix_mv_tournament_details_status",
        "mv_tournament_details",
        ["status"],
        schema="public_read",
    )
    op.create_index(
        "ix_mv_tournament_details_start_date",
        "mv_tournament_details",
        ["start_date"],
        schema="public_read",
    )

    # Create mv_match_details
    op.create_table(
        "mv_match_details",
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("tournament_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tournament_name", sa.String(), nullable=False),
        sa.Column("modality_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_name", sa.String(), nullable=True),
        sa.Column(
            "participants", postgresql.JSON(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("results", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("participant_count", sa.Integer(), nullable=False),
        sa.Column("comment_count", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("match_id"),
        schema="public_read",
    )
    op.create_index(
        "ix_mv_match_details_tournament_id",
        "mv_match_details",
        ["tournament_id"],
        schema="public_read",
    )
    op.create_index(
        "ix_mv_match_details_status",
        "mv_match_details",
        ["status"],
        schema="public_read",
    )
    op.create_index(
        "ix_mv_match_details_start_time",
        "mv_match_details",
        ["start_time"],
        schema="public_read",
    )

    # Create mv_tournament_standings
    op.create_table(
        "mv_tournament_standings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tournament_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("competitor_type", sa.String(), nullable=False),
        sa.Column(
            "competitor_entity_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("competitor_name", sa.String(), nullable=False),
        sa.Column("matches_played", sa.Integer(), nullable=False),
        sa.Column("wins", sa.Integer(), nullable=False),
        sa.Column("losses", sa.Integer(), nullable=False),
        sa.Column("draws", sa.Integer(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column(
            "statistics_metadata", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tournament_id", "competitor_entity_id", name="uq_tournament_standings"
        ),
        schema="public_read",
    )
    op.create_index(
        "ix_mv_tournament_standings_tournament_id",
        "mv_tournament_standings",
        ["tournament_id"],
        schema="public_read",
    )
    op.create_index(
        "ix_mv_tournament_standings_rank",
        "mv_tournament_standings",
        ["tournament_id", "rank"],
        schema="public_read",
    )


def downgrade() -> None:
    """
    Downgrade by reverting to the old schema.
    """

    # Drop new materialized views
    op.drop_index(
        "ix_mv_tournament_standings_rank",
        table_name="mv_tournament_standings",
        schema="public_read",
    )
    op.drop_index(
        "ix_mv_tournament_standings_tournament_id",
        table_name="mv_tournament_standings",
        schema="public_read",
    )
    op.drop_table("mv_tournament_standings", schema="public_read")

    op.drop_index(
        "ix_mv_match_details_start_time",
        table_name="mv_match_details",
        schema="public_read",
    )
    op.drop_index(
        "ix_mv_match_details_status",
        table_name="mv_match_details",
        schema="public_read",
    )
    op.drop_index(
        "ix_mv_match_details_tournament_id",
        table_name="mv_match_details",
        schema="public_read",
    )
    op.drop_table("mv_match_details", schema="public_read")

    op.drop_index(
        "ix_mv_tournament_details_start_date",
        table_name="mv_tournament_details",
        schema="public_read",
    )
    op.drop_index(
        "ix_mv_tournament_details_status",
        table_name="mv_tournament_details",
        schema="public_read",
    )
    op.drop_index(
        "ix_mv_tournament_details_modality_id",
        table_name="mv_tournament_details",
        schema="public_read",
    )
    op.drop_table("mv_tournament_details", schema="public_read")

    op.drop_index(
        "ix_mv_student_details_student_number",
        table_name="mv_student_details",
        schema="public_read",
    )
    op.drop_index(
        "ix_mv_student_details_course_id",
        table_name="mv_student_details",
        schema="public_read",
    )
    op.drop_table("mv_student_details", schema="public_read")

    op.drop_index(
        "ix_mv_team_details_modality_id",
        table_name="mv_team_details",
        schema="public_read",
    )
    op.drop_index(
        "ix_mv_team_details_course_id",
        table_name="mv_team_details",
        schema="public_read",
    )
    op.drop_table("mv_team_details", schema="public_read")

    # Drop new core tables
    op.drop_index(
        "ix_match_comments_match_id", table_name="match_comments", schema="public_read"
    )
    op.drop_table("match_comments", schema="public_read")

    op.drop_index(
        "ix_match_lineups_team_id", table_name="match_lineups", schema="public_read"
    )
    op.drop_index(
        "ix_match_lineups_match_id", table_name="match_lineups", schema="public_read"
    )
    op.drop_table("match_lineups", schema="public_read")

    op.drop_index(
        "ix_match_results_participant_id",
        table_name="match_results",
        schema="public_read",
    )
    op.drop_index(
        "ix_match_results_match_id", table_name="match_results", schema="public_read"
    )
    op.drop_table("match_results", schema="public_read")

    op.drop_index(
        "ix_match_participants_entity_id",
        table_name="match_participants",
        schema="public_read",
    )
    op.drop_index(
        "ix_match_participants_match_id",
        table_name="match_participants",
        schema="public_read",
    )
    op.drop_table("match_participants", schema="public_read")

    op.drop_index("ix_matches_start_time", table_name="matches", schema="public_read")
    op.drop_index("ix_matches_status", table_name="matches", schema="public_read")
    op.drop_index(
        "ix_matches_tournament_id", table_name="matches", schema="public_read"
    )
    op.drop_table("matches", schema="public_read")

    op.drop_index(
        "ix_tournament_competitors_entity_id",
        table_name="tournament_competitors",
        schema="public_read",
    )
    op.drop_index(
        "ix_tournament_competitors_tournament_id",
        table_name="tournament_competitors",
        schema="public_read",
    )
    op.drop_table("tournament_competitors", schema="public_read")

    op.drop_table("tournaments", schema="public_read")

    op.drop_index(
        "ix_team_players_student_id", table_name="team_players", schema="public_read"
    )
    op.drop_index(
        "ix_team_players_team_id", table_name="team_players", schema="public_read"
    )
    op.drop_table("team_players", schema="public_read")

    op.drop_table("teams", schema="public_read")
    op.drop_table("staff", schema="public_read")
    op.drop_table("students", schema="public_read")
    op.drop_table("modalities", schema="public_read")
    op.drop_table("modality_types", schema="public_read")
    op.drop_table("courses", schema="public_read")
    op.drop_table("nucleos", schema="public_read")

    # Drop enums
    sa.Enum(name="matchstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="participanttype").drop(op.get_bind(), checkfirst=True)

    # Recreate old tables (from 4e8c9a5b7f2d migration)
    # Nucleo
    op.create_table(
        "nucleos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("abbreviation", sa.String(length=10), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Courses
    op.create_table(
        "courses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nucleo_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("abbreviation", sa.String(length=10), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["nucleo_id"], ["public_read.nucleos.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Modality types
    op.create_table(
        "modality_types",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("escaloes", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Modalities
    op.create_table(
        "modalities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("modality_type_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["modality_type_id"], ["public_read.modality_types.id"]
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Students
    op.create_table(
        "students",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=True),
        sa.Column("student_number", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("is_member", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["course_id"], ["public_read.courses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_number"),
        schema="public_read",
    )

    # Staff
    op.create_table(
        "staff",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("staff_number", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("contact", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("staff_number"),
        schema="public_read",
    )

    # Teams
    op.create_table(
        "teams",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("modality_id", sa.UUID(), nullable=True),
        sa.Column("course_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["course_id"], ["public_read.courses.id"]),
        sa.ForeignKeyConstraint(["modality_id"], ["public_read.modalities.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Team players
    op.create_table(
        "team_players",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("team_id", sa.UUID(), nullable=True),
        sa.Column("student_id", sa.UUID(), nullable=True),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("removed_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["public_read.students.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["public_read.teams.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Tournaments
    op.create_table(
        "tournaments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("modality_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["modality_id"], ["public_read.modalities.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Tournament competitors
    op.create_table(
        "tournament_competitors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tournament_id", sa.UUID(), nullable=True),
        sa.Column("competitor_type", sa.String(length=10), nullable=True),
        sa.Column("competitor_entity_id", sa.UUID(), nullable=True),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("removed_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["tournament_id"], ["public_read.tournaments.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Matches
    op.create_table(
        "matches",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tournament_id", sa.UUID(), nullable=True),
        sa.Column("location", sa.Text(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("team_home_id", sa.UUID(), nullable=True),
        sa.Column("team_away_id", sa.UUID(), nullable=True),
        sa.Column("team_home_name", sa.String(length=100), nullable=True),
        sa.Column("team_away_name", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["tournament_id"], ["public_read.tournaments.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Match participants
    op.create_table(
        "match_participants",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("match_id", sa.UUID(), nullable=True),
        sa.Column("participant_type", sa.String(length=10), nullable=True),
        sa.Column("participant_entity_id", sa.UUID(), nullable=True),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("removed_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["public_read.matches.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Match results
    op.create_table(
        "match_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("match_id", sa.UUID(), nullable=True),
        sa.Column("participant_id", sa.UUID(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("results_metadata", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["public_read.matches.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Match lineups
    op.create_table(
        "match_lineups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("match_id", sa.UUID(), nullable=True),
        sa.Column("team_id", sa.UUID(), nullable=False),
        sa.Column("player_id", sa.UUID(), nullable=True),
        sa.Column("jersey_number", sa.Integer(), nullable=False),
        sa.Column("is_starter", sa.Boolean(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["public_read.matches.id"]),
        sa.ForeignKeyConstraint(["player_id"], ["public_read.students.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Match comments
    op.create_table(
        "match_comments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("match_id", sa.UUID(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["public_read.matches.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )

    # Recreate old views
    op.create_table(
        "games_view",
        sa.Column("game_id", sa.UUID(), nullable=False),
        sa.Column("tournament_id", sa.UUID(), nullable=True),
        sa.Column("tournament_name", sa.Text(), nullable=True),
        sa.Column("tournament_status", sa.Text(), nullable=True),
        sa.Column("modality_id", sa.UUID(), nullable=True),
        sa.Column("modality_name", sa.Text(), nullable=True),
        sa.Column("modality_type_name", sa.Text(), nullable=True),
        sa.Column("team_a_id", sa.UUID(), nullable=True),
        sa.Column("team_a_name", sa.Text(), nullable=True),
        sa.Column("team_a_course", sa.Text(), nullable=True),
        sa.Column("team_b_id", sa.UUID(), nullable=True),
        sa.Column("team_b_name", sa.Text(), nullable=True),
        sa.Column("team_b_course", sa.Text(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("score", sa.Text(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("state", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("game_id"),
        schema="public_read",
    )

    op.create_table(
        "tournament_view",
        sa.Column("tournament_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=True),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("modality_id", sa.UUID(), nullable=True),
        sa.Column("modality_name", sa.Text(), nullable=True),
        sa.Column("modality_type_name", sa.Text(), nullable=True),
        sa.Column("total_competitors", sa.Integer(), nullable=True),
        sa.Column("total_matches", sa.Integer(), nullable=True),
        sa.Column("completed_matches", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("tournament_id"),
        schema="public_read",
    )

    op.create_table(
        "ranking_view",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tournament_id", sa.UUID(), nullable=False),
        sa.Column("team_id", sa.UUID(), nullable=False),
        sa.Column("team_name", sa.Text(), nullable=False),
        sa.Column("course_name", sa.Text(), nullable=True),
        sa.Column("course_abbreviation", sa.Text(), nullable=True),
        sa.Column("nucleo_name", sa.Text(), nullable=True),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("matches_played", sa.Integer(), nullable=True),
        sa.Column("matches_won", sa.Integer(), nullable=True),
        sa.Column("matches_lost", sa.Integer(), nullable=True),
        sa.Column("matches_drawn", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )
