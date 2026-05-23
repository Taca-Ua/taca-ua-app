"""Add nucleo admin ids field

Revision ID: 003
Revises: 002
Create Date: 2026-03-02

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # default value is set to empty list
    op.add_column(
        "nucleo",
        sa.Column(
            "admins_ids",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        schema="modalities",
    )


def downgrade() -> None:
    op.drop_column("nucleo", "admins_ids", schema="modalities")
