"""Add tournament_competitor_type to modality_type

Revision ID: 007
Revises: 006
Create Date: 2026-03-02

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "modality_type",
        sa.Column("tournament_competitor_type", sa.Text(), nullable=True),
        schema="modalities",
    )


def downgrade() -> None:
    op.drop_column("modality_type", "tournament_competitor_type")
