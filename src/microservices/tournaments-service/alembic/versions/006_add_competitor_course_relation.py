"""Add competitor_course_id to tournament_competitor

Revision ID: 006
Revises: 005
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "006"
down_revision: Union[str, Sequence[str], None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add competitor_course_id to tournament_competitor."""

    op.add_column(
        "tournament_competitor",
        sa.Column("competitor_course_id", UUID(as_uuid=True), nullable=True),
        schema="tournaments",
    )

    op.create_index(
        op.f("ix_tournaments_tournament_competitor_competitor_course_id"),
        "tournament_competitor",
        ["competitor_course_id"],
        unique=False,
        schema="tournaments",
    )


def downgrade() -> None:
    """Remove competitor_course_id from tournament_competitor."""

    op.drop_index(
        op.f("ix_tournaments_tournament_competitor_competitor_course_id"),
        table_name="tournament_competitor",
        schema="tournaments",
    )

    op.drop_column(
        "tournament_competitor",
        "competitor_course_id",
        schema="tournaments",
    )
