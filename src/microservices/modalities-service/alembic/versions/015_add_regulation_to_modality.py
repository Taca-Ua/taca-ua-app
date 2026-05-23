"""add regulation to modality

Revision ID: 015
Revises: 014
Create Date: 2026-05-22 09:17:00.798776

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "015"
down_revision: Union[str, Sequence[str], None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "season_modality",
        sa.Column(
            "regulation_id",
            sa.UUID(),
            sa.ForeignKey("modalities.regulation.id"),
            nullable=True,
        ),
        schema="modalities",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("season_modality", "regulation_id", schema="modalities")
