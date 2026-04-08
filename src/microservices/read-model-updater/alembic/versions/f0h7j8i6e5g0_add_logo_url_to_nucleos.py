"""Add logo_url to nucleos table

Revision ID: f0h7j8i6e5g0
Revises: d8f5h6g4c3e8
Create Date: 2026-04-08 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f0h7j8i6e5g0"
down_revision: Union[str, Sequence[str], None] = "d8f5h6g4c3e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "nucleos",
        sa.Column("logo_url", sa.Text(), nullable=True),
        schema="public_read",
    )


def downgrade() -> None:
    op.drop_column("nucleos", "logo_url", schema="public_read")
