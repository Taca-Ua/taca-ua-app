"""TUA-142: Add comprehensive read models for all events

Revision ID: 4e8c9a5b7f2d
Revises: 9c2d6e7664af
Create Date: 2026-02-12 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4e8c9a5b7f2d"
down_revision: Union[str, Sequence[str], None] = "9c2d6e7664af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema by adding comprehensive read models."""
    
    # Create nucleo table
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
    
    # Create courses table
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
    
    # Create modality_types table
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
    
    # Create modalities table
    op.create_table(
        "modalities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("modality_type_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["modality_type_id"], ["public_read.modality_types.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="public_read",
    )
    
    # Create students table
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
    
    # Create staff table
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
    
    # Create teams table
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
    
    # Create team_players table
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
    
    # Create tournaments table
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
    
    # Create tournament_competitors table
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
    
    # Create matches table
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
    
    # Create match_participants table
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
    
    # Create match_results table
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
    
    # Create match_lineups table
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
    
    # Create match_comments table
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
    
    # Update existing views with enhanced structure
    
    # Drop and recreate games_view with enhanced columns
    op.drop_table("games_view", schema="public_read")
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
    
    # Drop and recreate tournament_view with enhanced columns
    op.drop_table("tournament_view", schema="public_read")
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
    
    # Drop and recreate ranking_view with enhanced columns
    op.drop_table("ranking_view", schema="public_read")
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


def downgrade() -> None:
    """Downgrade schema by removing comprehensive read models."""
    
    # Drop new tables in reverse order
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
    
    # Restore original view structure
    op.drop_table("ranking_view", schema="public_read")
    op.drop_table("tournament_view", schema="public_read")
    op.drop_table("games_view", schema="public_read")
    
    # Recreate original tables
    op.create_table(
        "games_view",
        sa.Column("game_id", sa.UUID(), nullable=False),
        sa.Column("tournament_name", sa.Text(), nullable=True),
        sa.Column("modality_name", sa.Text(), nullable=True),
        sa.Column("team_a_name", sa.Text(), nullable=True),
        sa.Column("team_b_name", sa.Text(), nullable=True),
        sa.Column("score", sa.Text(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("state", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("game_id"),
        schema="public_read",
    )
    op.create_table(
        "ranking_view",
        sa.Column("tournament_id", sa.UUID(), nullable=False),
        sa.Column("team", sa.Text(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("tournament_id", "team"),
        schema="public_read",
    )
    op.create_table(
        "tournament_view",
        sa.Column("tournament_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("modality", sa.Text(), nullable=True),
        sa.Column("stage_count", sa.Integer(), nullable=True),
        sa.Column("total_matches", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("tournament_id"),
        schema="public_read",
    )