"""TUA-160: Rename team_id to competitor_id in tournament_ranking_position

Revision ID: f9g6h7i5d4j9
Revises: ebe27bde493d
Create Date: 2026-03-04 11:30:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f9g6h7i5d4j9"
down_revision: Union[str, Sequence[str], None] = "ebe27bde493d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Rename team_id to competitor_id to support both team and athlete competitions.
    """

    # Drop the old unique constraint
    op.drop_constraint(
        "uq_tournament_team", "tournament_ranking_position", schema="tournaments"
    )

    # Drop the old index on team_id
    op.drop_index(
        op.f("ix_tournaments_tournament_ranking_position_team_id"),
        table_name="tournament_ranking_position",
        schema="tournaments",
    )

    # Rename the column
    op.alter_column(
        "tournament_ranking_position",
        "team_id",
        new_column_name="competitor_id",
        schema="tournaments",
    )

    # Create the new index on competitor_id
    op.create_index(
        op.f("ix_tournaments_tournament_ranking_position_competitor_id"),
        "tournament_ranking_position",
        ["competitor_id"],
        unique=False,
        schema="tournaments",
    )

    # Create the new unique constraint
    op.create_unique_constraint(
        "uq_tournament_competitor",
        "tournament_ranking_position",
        ["tournament_id", "competitor_id"],
        schema="tournaments",
    )


def downgrade() -> None:
    """
    Revert competitor_id back to team_id.
    """

    # Drop the new unique constraint
    op.drop_constraint(
        "uq_tournament_competitor", "tournament_ranking_position", schema="tournaments"
    )

    # Drop the new index on competitor_id
    op.drop_index(
        op.f("ix_tournaments_tournament_ranking_position_competitor_id"),
        table_name="tournament_ranking_position",
        schema="tournaments",
    )

    # Rename the column back
    op.alter_column(
        "tournament_ranking_position",
        "competitor_id",
        new_column_name="team_id",
        schema="tournaments",
    )

    # Recreate the old index on team_id
    op.create_index(
        op.f("ix_tournaments_tournament_ranking_position_team_id"),
        "tournament_ranking_position",
        ["team_id"],
        unique=False,
        schema="tournaments",
    )

    # Recreate the old unique constraint
    op.create_unique_constraint(
        "uq_tournament_team",
        "tournament_ranking_position",
        ["tournament_id", "team_id"],
        schema="tournaments",
    )
