"""add season relation to regulations

Revision ID: 013
Revises: 012
Create Date: 2026-05-09 18:24:15.147284

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "013"
down_revision: Union[str, Sequence[str], None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "regulation",
        sa.Column(
            "season_id",
            sa.Integer(),
            nullable=True,
            index=True,
        ),
        schema="modalities",
    )
    op.execute(
        """
        UPDATE modalities.regulation
        SET season_id = (
            SELECT id FROM modalities.season WHERE finished_by IS NULL LIMIT 1
        )
        WHERE season_id IS NULL
        """
    )
    op.alter_column(
        "regulation",
        "season_id",
        nullable=False,  # Set to False after populating existing records
        schema="modalities",
    )
    op.create_foreign_key(
        "fk_regulation_season",
        "regulation",
        "season",
        ["season_id"],
        ["id"],
        source_schema="modalities",
        referent_schema="modalities",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_regulation_season", "regulation", schema="modalities", type_="foreignkey"
    )
    op.drop_column("regulation", "season_id", schema="modalities")
