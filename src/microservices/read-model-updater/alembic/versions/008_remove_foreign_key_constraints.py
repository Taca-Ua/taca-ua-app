"""Remove foreign key constraints for eventual consistency

Revision ID: 008
Revises: 007
Create Date: 2026-03-20

This migration removes all foreign key constraints from the read model tables
to support eventual consistency in event-sourced architecture. FK constraints
are being removed because events may arrive out of order (e.g., match created
before tournament exists).

Relationships are preserved in SQLAlchemy models for query navigation,
but database-level referential integrity is relaxed.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Union[str, Sequence[str], None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop all foreign key constraints from read model tables."""

    # Course table
    op.drop_constraint(
        "courses_nucleo_id_fkey",
        "courses",
        schema="public_read",
        type_="foreignkey",
    )

    # Student table
    op.drop_constraint(
        "students_course_id_fkey",
        "students",
        schema="public_read",
        type_="foreignkey",
    )

    # Modality table
    op.drop_constraint(
        "modalities_modality_type_id_fkey",
        "modalities",
        schema="public_read",
        type_="foreignkey",
    )

    # Team table (2 FKs)
    op.drop_constraint(
        "teams_course_id_fkey",
        "teams",
        schema="public_read",
        type_="foreignkey",
    )
    op.drop_constraint(
        "teams_modality_id_fkey",
        "teams",
        schema="public_read",
        type_="foreignkey",
    )

    # TeamPlayer table (2 FKs)
    op.drop_constraint(
        "team_players_team_id_fkey",
        "team_players",
        schema="public_read",
        type_="foreignkey",
    )
    op.drop_constraint(
        "team_players_student_id_fkey",
        "team_players",
        schema="public_read",
        type_="foreignkey",
    )

    # Tournament table
    op.drop_constraint(
        "tournaments_modality_id_fkey",
        "tournaments",
        schema="public_read",
        type_="foreignkey",
    )

    # TournamentCompetitor table
    op.drop_constraint(
        "tournament_competitors_tournament_id_fkey",
        "tournament_competitors",
        schema="public_read",
        type_="foreignkey",
    )

    # TournamentRanking table
    op.drop_constraint(
        "tournament_rankings_tournament_id_fkey",
        "tournament_rankings",
        schema="public_read",
        type_="foreignkey",
    )

    # Match table
    op.drop_constraint(
        "matches_tournament_id_fkey",
        "matches",
        schema="public_read",
        type_="foreignkey",
    )

    # MatchParticipant table
    op.drop_constraint(
        "match_participants_match_id_fkey",
        "match_participants",
        schema="public_read",
        type_="foreignkey",
    )

    # MatchResult table (2 FKs)
    op.drop_constraint(
        "match_results_match_id_fkey",
        "match_results",
        schema="public_read",
        type_="foreignkey",
    )
    # op.drop_constraint(
    #     "match_results_participant_id_fkey",
    #     "match_results",
    #     schema="public_read",
    #     type_="foreignkey",
    # )

    # MatchLineup table
    op.drop_constraint(
        "match_lineups_match_id_fkey",
        "match_lineups",
        schema="public_read",
        type_="foreignkey",
    )

    # MatchComment table
    op.drop_constraint(
        "match_comments_match_id_fkey",
        "match_comments",
        schema="public_read",
        type_="foreignkey",
    )

    # Note: general_rankings and modality_rankings tables were created without
    # FK constraints in migration 006, so no constraints to drop for them.


def downgrade() -> None:
    """Recreate all foreign key constraints."""

    # Course table
    op.create_foreign_key(
        "courses_nucleo_id_fkey",
        "courses",
        "nucleos",
        ["nucleo_id"],
        ["nucleo_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )

    # Student table
    op.create_foreign_key(
        "students_course_id_fkey",
        "students",
        "courses",
        ["course_id"],
        ["course_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )

    # Modality table
    op.create_foreign_key(
        "modalities_modality_type_id_fkey",
        "modalities",
        "modality_types",
        ["modality_type_id"],
        ["modality_type_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )

    # Team table (2 FKs)
    op.create_foreign_key(
        "teams_course_id_fkey",
        "teams",
        "courses",
        ["course_id"],
        ["course_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )
    op.create_foreign_key(
        "teams_modality_id_fkey",
        "teams",
        "modalities",
        ["modality_id"],
        ["modality_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )

    # TeamPlayer table (2 FKs)
    op.create_foreign_key(
        "team_players_team_id_fkey",
        "team_players",
        "teams",
        ["team_id"],
        ["team_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )
    op.create_foreign_key(
        "team_players_student_id_fkey",
        "team_players",
        "students",
        ["student_id"],
        ["student_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )

    # Tournament table
    op.create_foreign_key(
        "tournaments_modality_id_fkey",
        "tournaments",
        "modalities",
        ["modality_id"],
        ["modality_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )

    # TournamentCompetitor table
    op.create_foreign_key(
        "tournament_competitors_tournament_id_fkey",
        "tournament_competitors",
        "tournaments",
        ["tournament_id"],
        ["tournament_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )

    # TournamentRanking table
    op.create_foreign_key(
        "tournament_rankings_tournament_id_fkey",
        "tournament_rankings",
        "tournaments",
        ["tournament_id"],
        ["tournament_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )

    # Match table
    op.create_foreign_key(
        "matches_tournament_id_fkey",
        "matches",
        "tournaments",
        ["tournament_id"],
        ["tournament_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )

    # MatchParticipant table
    op.create_foreign_key(
        "match_participants_match_id_fkey",
        "match_participants",
        "matches",
        ["match_id"],
        ["match_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )

    # MatchResult table (2 FKs)
    op.create_foreign_key(
        "match_results_match_id_fkey",
        "match_results",
        "matches",
        ["match_id"],
        ["match_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )
    # op.create_foreign_key(
    #     "match_results_participant_id_fkey",
    #     "match_results",
    #     "match_participants",
    #     ["participant_id"],
    #     ["participant_id"],
    #     source_schema="public_read",
    #     referent_schema="public_read",
    # )

    # MatchLineup table
    op.create_foreign_key(
        "match_lineups_match_id_fkey",
        "match_lineups",
        "matches",
        ["match_id"],
        ["match_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )

    # MatchComment table
    op.create_foreign_key(
        "match_comments_match_id_fkey",
        "match_comments",
        "matches",
        ["match_id"],
        ["match_id"],
        source_schema="public_read",
        referent_schema="public_read",
    )
