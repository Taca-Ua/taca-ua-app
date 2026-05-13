"""add field for team lineage tracking

Revision ID: 011
Revises: 010
Create Date: 2026-04-30 00:14:46.838399

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "011"
down_revision: Union[str, Sequence[str], None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "team",
        sa.Column("derived_from_team_id", sa.UUID(), nullable=True),
        schema="modalities",
    )
    op.create_foreign_key(
        "fk_teams_derived_from_team_id",
        "team",
        "team",
        ["derived_from_team_id"],
        ["id"],
        source_schema="modalities",
        referent_schema="modalities",
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_teams_derived_from_team_id",
        "team",
        ["derived_from_team_id"],
        unique=False,
        schema="modalities",
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_teams_derived_from_team_id", schema="modalities")
    op.drop_constraint("fk_teams_derived_from_team_id", "team", schema="modalities")
    op.drop_column("team", "derived_from_team_id", schema="modalities")
