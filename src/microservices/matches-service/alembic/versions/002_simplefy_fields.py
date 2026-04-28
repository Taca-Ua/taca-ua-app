"""simplefie fields

Revision ID: 002
Revises: 001
Create Date: 2026-04-01 17:11:36.800403

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = ("yolo-refactor",)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Set tournament_id to NOT NULL
    op.alter_column(
        "match",
        "tournament_id",
        schema="matches",
        nullable=False,
    )

    # --- MATCH_PARTICIPANT ---
    # Drop old PK and columns
    with op.batch_alter_table("match_participant", schema="matches") as batch_op:
        batch_op.drop_constraint("match_participant_pkey", type_="primary")
        batch_op.drop_column("id")
        batch_op.drop_column("participant_type")
        batch_op.drop_column("team_id")
        batch_op.drop_column("athlete_id")
        batch_op.drop_column("result_metadata")

        # Remove indexes
        # batch_op.drop_index("ix_matches_match_participant_team_id")
        # batch_op.drop_index("ix_matches_match_participant_athlete_id")

        # Add participant column
        batch_op.add_column(
            sa.Column("participant", sa.UUID(), nullable=False, primary_key=True)
        )
        batch_op.create_index(
            "ix_matches_match_participant_participant", ["participant"], unique=False
        )

        # Add new PK
        batch_op.create_primary_key("pk_match_participant", ["match_id", "participant"])

    # --- LINEUP ---
    with op.batch_alter_table("lineup", schema="matches") as batch_op:
        batch_op.drop_constraint("lineup_pkey", type_="primary")
        batch_op.drop_column("id")
        batch_op.drop_column("team_id")

        # Remove indexes
        # batch_op.drop_index("ix_matches_lineup_team_id")

        # Add participant column
        batch_op.add_column(
            sa.Column("participant", sa.UUID(), nullable=False, primary_key=True)
        )

        # Change jersey_number and is_starter to nullable
        batch_op.alter_column("jersey_number", nullable=True)
        batch_op.alter_column("is_starter", nullable=True)

        # Add composite PK
        batch_op.create_primary_key(
            "pk_lineup", ["match_id", "participant", "player_id"]
        )

    # Remove old indexes if they exist
    try:
        op.drop_index(
            "ix_matches_lineup_player_id", table_name="lineup", schema="matches"
        )
    except Exception:
        pass
    try:
        op.drop_index(
            "ix_matches_match_participant_match_id",
            table_name="match_participant",
            schema="matches",
        )
    except Exception:
        pass


def downgrade() -> None:
    """Downgrade schema."""
    # Revert tournament_id to nullable
    op.alter_column(
        "match",
        "tournament_id",
        schema="matches",
        nullable=True,
    )

    # --- MATCH_PARTICIPANT ---
    with op.batch_alter_table("match_participant", schema="matches") as batch_op:
        batch_op.drop_constraint("pk_match_participant", type_="primary")
        batch_op.drop_index("ix_matches_match_participant_participant")
        batch_op.drop_column("participant")
        # Restore old columns (will be NULL)
        batch_op.add_column(sa.Column("id", sa.UUID(), primary_key=True))
        batch_op.add_column(
            sa.Column(
                "participant_type",
                sa.Enum(
                    "TEAM", "ATHLETE", name="participant_type", inherit_schema=True
                ),
                nullable=True,
            )
        )
        batch_op.add_column(sa.Column("team_id", sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column("athlete_id", sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column("result_metadata", sa.JSON(), nullable=True))
        # Restore PK
        batch_op.create_primary_key("pk_match_participant_id", ["id"])
        # Restore indexes
        batch_op.create_index(
            "ix_matches_match_participant_team_id", ["team_id"], unique=False
        )
        batch_op.create_index(
            "ix_matches_match_participant_athlete_id", ["athlete_id"], unique=False
        )

    # --- LINEUP ---
    with op.batch_alter_table("lineup", schema="matches") as batch_op:
        batch_op.drop_constraint("pk_lineup", type_="primary")
        batch_op.drop_column("participant")
        # Restore old columns (will be NULL)
        batch_op.add_column(sa.Column("id", sa.UUID(), primary_key=True))
        batch_op.add_column(sa.Column("team_id", sa.UUID(), nullable=True))
        # Restore PK
        batch_op.create_primary_key("pk_lineup_id", ["id"])
        # Restore indexes
        batch_op.create_index("ix_matches_lineup_team_id", ["team_id"], unique=False)
        batch_op.create_index(
            "ix_matches_lineup_player_id", ["player_id"], unique=False
        )
        # Revert jersey_number and is_starter to NOT NULL
        batch_op.alter_column("jersey_number", nullable=False)
        batch_op.alter_column("is_starter", nullable=False)
