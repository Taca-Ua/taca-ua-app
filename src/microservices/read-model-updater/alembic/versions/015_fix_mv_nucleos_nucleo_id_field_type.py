"""fix mv_nucleos.nucleo_id field type

Revision ID: 015
Revises: 014
Create Date: 2026-04-28 02:30:49.983304

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
    # Alter nucleo_id column type from String to UUID in mv_nucleo_details
    op.alter_column(
        "mv_nucleo_details",
        "nucleo_id",
        type_=sa.UUID(),
        existing_type=sa.String(),
        schema="public_read",
        postgresql_using="nucleo_id::uuid",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "mv_nucleo_details",
        "nucleo_id",
        type_=sa.String(),
        existing_type=sa.UUID(),
        schema="public_read",
    )
