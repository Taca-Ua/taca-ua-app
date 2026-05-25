"""add mode field to modality_type

Revision ID: 014
Revises: 013
Create Date: 2026-05-14 16:01:05.346458

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "014"
down_revision: Union[str, Sequence[str], None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "modality_type",
        sa.Column(
            "mode", sa.Text(), nullable=False, server_default=sa.text("'modality'")
        ),
        schema="modalities",
    )
    op.drop_column("modality_type", "is_playoff", schema="modalities")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("modality_type", "mode", schema="modalities")
    op.add_column(
        "modality_type",
        sa.Column(
            "is_playoff", sa.BOOLEAN(), nullable=False, server_default=sa.text("false")
        ),
        schema="modalities",
    )
