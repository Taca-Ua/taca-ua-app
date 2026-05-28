"""add scored points fields in league

Revision ID: 009
Revises: 008
Create Date: 2026-05-21 20:08:41.561508

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: Union[str, Sequence[str], None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "league_standings",
        sa.Column("scored_points", sa.Integer(), nullable=True, server_default="0"),
        schema="tournaments",
    )
    op.add_column(
        "league_standings",
        sa.Column("conceded_points", sa.Integer(), nullable=True, server_default="0"),
        schema="tournaments",
    )

    # go through existing matches and update scored_points and conceded_points for each competitor in league_standings
    connection = op.get_bind()
    result = connection.execute(
        sa.text(
            """
            SELECT m.tournament_id, m.results
            FROM tournaments.league_matches m
            JOIN tournaments.league_tournaments t ON m.tournament_id = t.id
            """
        )
    )
    tourn_comp_map = {}
    for row in result:
        tournament_id, results = row
        if not results:
            continue

        if tournament_id not in tourn_comp_map:
            tourn_comp_map[tournament_id] = {}

        # Update scored_points and conceded_points for each competitor in the match results
        for competitor_id, res in results.items():
            score = res.get("score", 0) or 0
            if competitor_id not in tourn_comp_map[tournament_id]:
                tourn_comp_map[tournament_id][competitor_id] = {
                    "scored_points": 0,
                    "conceded_points": 0,
                }

            tourn_comp_map[tournament_id][competitor_id] = {
                "scored_points": tourn_comp_map[tournament_id][competitor_id][
                    "scored_points"
                ]
                + score,
                "conceded_points": tourn_comp_map[tournament_id][competitor_id][
                    "conceded_points"
                ]
                + sum(
                    r.get("score", 0) or 0
                    for cid, r in results.items()
                    if cid != competitor_id
                ),
            }

    for tournament_id in tourn_comp_map:
        for competitor_id, points in tourn_comp_map[tournament_id].items():
            connection.execute(
                sa.text(
                    """
                    UPDATE tournaments.league_standings
                    SET scored_points = scored_points + :scored_points,
                        conceded_points = conceded_points + :conceded_points
                    WHERE tournament_id = :tournament_id AND competitor_id = :competitor_id
                    """
                ),
                {
                    "scored_points": points["scored_points"],
                    "conceded_points": points["conceded_points"],
                    "tournament_id": tournament_id,
                    "competitor_id": competitor_id,
                },
            )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("league_standings", "scored_points", schema="tournaments")
    op.drop_column("league_standings", "conceded_points", schema="tournaments")
