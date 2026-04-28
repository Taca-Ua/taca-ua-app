"""add logo url to nucleos

Revision ID: 008
Revises: 007
Create Date: 2026-04-27 11:31:56.749727

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Union[str, Sequence[str], None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "nucleo", sa.Column("logo_url", sa.Text(), nullable=True), schema="modalities"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("nucleo", "logo_url", schema="modalities")
