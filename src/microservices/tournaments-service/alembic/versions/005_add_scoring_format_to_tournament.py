"""Add scoring format to tournament

Revision ID: 005
revises: f9g6h7i5d4j9
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "005"
down_revision: Union[str, Sequence[str], None] = "f9g6h7i5d4j9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add scoring_format_id to tournament to support different scoring formats (regular vs playoff).
    """

    op.add_column(
        "tournament",
        sa.Column("scoring_format_id", UUID(as_uuid=True), nullable=True, index=True),
        schema="tournaments",
    )


def downgrade() -> None:
    """
    Remove scoring_format_id from tournament.
    """

    op.drop_column("tournament", "scoring_format_id", schema="tournaments")
