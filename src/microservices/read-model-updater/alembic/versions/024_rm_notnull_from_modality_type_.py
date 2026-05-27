"""rm notnull from modality type description

Revision ID: 024
Revises: 023
Create Date: 2026-05-27 10:32:06.868533

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "024"
down_revision: Union[str, Sequence[str], None] = "023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "modality_types",
        "description",
        existing_type=sa.Text(),
        nullable=True,
        schema="public_read",
    )


def downgrade() -> None:
    """Downgrade schema."""
    # pass null values to empty string before altering the column to not nullable
    op.execute(
        "UPDATE public_read.modality_types SET description = '' WHERE description IS NULL"
    )
    op.alter_column(
        "modality_types",
        "description",
        existing_type=sa.Text(),
        nullable=False,
        schema="public_read",
    )
