"""add match staff table

Revision ID: 005
Revises: 004
Create Date: 2026-05-21 23:05:04.950320

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, Sequence[str], None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "lineup_staff",
        sa.Column("match_id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("participant_id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("staff_id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["match_id"], ["matches.match.id"], ondelete="CASCADE"),
        schema="matches",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("lineup_staff", schema="matches")
