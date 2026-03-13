"""Add is playoff field to modality_type

Revision ID: 004
Revises: 003
Create Date: 2026-03-02

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # default value is set to empty list
    op.add_column(
        "modality_type",
        sa.Column(
            "is_playoff",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        schema="modalities",
    )


def downgrade() -> None:
    op.drop_column("modality_type", "is_playoff", schema="modalities")
