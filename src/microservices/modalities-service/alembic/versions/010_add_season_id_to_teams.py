"""add season_id to teams

Revision ID: 010
Revises: 009
Create Date: 2026-04-29 21:38:07.959784

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010"
down_revision: Union[str, Sequence[str], None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "team", sa.Column("season_id", sa.Integer(), nullable=True), schema="modalities"
    )
    op.create_foreign_key(
        "fk_teams_season_id",
        "team",
        "season",
        ["season_id"],
        ["id"],
        source_schema="modalities",
        referent_schema="modalities",
    )
    op.create_index("ix_teams_season_id", "team", ["season_id"], schema="modalities")

    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_teams_season_id", table_name="team", schema="modalities")
    op.drop_constraint(
        "fk_teams_season_id", "team", schema="modalities", type_="foreignkey"
    )
    op.drop_column("team", "season_id", schema="modalities")
    pass
