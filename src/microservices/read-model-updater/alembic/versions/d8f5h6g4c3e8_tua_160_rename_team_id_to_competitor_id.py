"""TUA-160: Rename team_id to competitor_id in tournament_rankings

Revision ID: d8f5h6g4c3e8
Revises: c7e4g5f3b2d7
Create Date: 2026-03-04 11:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d8f5h6g4c3e8"
down_revision: Union[str, Sequence[str], None] = "c7e4g5f3b2d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Rename team_id to competitor_id to support both team and athlete competitions.
    """

    # Drop the old unique constraint
    op.drop_constraint(
        "uq_tournament_ranking", "tournament_rankings", schema="public_read"
    )

    # Rename the column
    op.alter_column(
        "tournament_rankings",
        "team_id",
        new_column_name="competitor_id",
        schema="public_read",
    )

    # Create the new unique constraint
    op.create_unique_constraint(
        "uq_tournament_ranking_competitor",
        "tournament_rankings",
        ["tournament_id", "competitor_id"],
        schema="public_read",
    )


def downgrade() -> None:
    """
    Revert competitor_id back to team_id.
    """

    # Drop the new unique constraint
    op.drop_constraint(
        "uq_tournament_ranking_competitor", "tournament_rankings", schema="public_read"
    )

    # Rename the column back
    op.alter_column(
        "tournament_rankings",
        "competitor_id",
        new_column_name="team_id",
        schema="public_read",
    )

    # Recreate the old unique constraint
    op.create_unique_constraint(
        "uq_tournament_ranking",
        "tournament_rankings",
        ["tournament_id", "team_id"],
        schema="public_read",
    )
