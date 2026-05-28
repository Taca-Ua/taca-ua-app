"""add nucleo logo url to team

Revision ID: 023
Revises: 022
Create Date: 2026-05-27 10:25:43.330686

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "023"
down_revision: Union[str, Sequence[str], None] = "022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "mv_team_details",
        sa.Column("nucleo_logo_url", sa.String(length=500), nullable=True),
        schema="public_read",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("mv_team_details", "nucleo_logo_url", schema="public_read")
