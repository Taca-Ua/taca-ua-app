"""
Update match participant logic - remove deprecated fields

Revision ID: 011
Revises: 010
Create Date: 2026-04-27

Changes:
- Remove participant_type column (no longer needed, now get from TournamentCompetitor)
- Remove participant_entity_id column (no longer needed, now get from TournamentCompetitor)
- Remove unique constraint on participant_id (keep only composite unique on match_id, participant_id)
- Remove index on participant_entity_id
- participant_id is now the competitor_id from TournamentCompetitor
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: Union[str, Sequence[str], None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the index on participant_entity_id
    op.drop_index(
        "ix_match_participants_entity_id",
        table_name="match_participants",
        schema="public_read",
    )

    # Drop the unique constraint on participant_id column
    # PostgreSQL names this as {table}_{column}_key
    op.drop_constraint(
        "match_participants_participant_id_key",
        "match_participants",
        schema="public_read",
        type_="unique",
    )

    # Drop participant_type column
    op.drop_column(
        "match_participants",
        "participant_type",
        schema="public_read",
    )

    # Drop participant_entity_id column
    op.drop_column(
        "match_participants",
        "participant_entity_id",
        schema="public_read",
    )


def downgrade() -> None:
    # Recreate participant_entity_id column
    op.add_column(
        "match_participants",
        sa.Column(
            "participant_entity_id",
            sa.UUID(),
            nullable=False,
        ),
        schema="public_read",
    )

    # Recreate participant_type column as Enum
    op.add_column(
        "match_participants",
        sa.Column(
            "participant_type",
            sa.Enum("team", "athlete", name="participanttype"),
            nullable=False,
        ),
        schema="public_read",
    )

    # Recreate the index on participant_entity_id
    op.create_index(
        "ix_match_participants_entity_id",
        "match_participants",
        ["participant_entity_id"],
        schema="public_read",
    )

    # Recreate the unique constraint on participant_id
    op.create_unique_constraint(
        "match_participants_participant_id_key",
        "match_participants",
        ["participant_id"],
        schema="public_read",
    )
