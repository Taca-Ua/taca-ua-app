"""Add competitor_course_id to tournament_competitors

Revision ID: 002
Revises: 001
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add competitor_course_id to tournament_competitors."""

    op.add_column(
        "tournament_competitors",
        sa.Column("competitor_course_id", UUID(as_uuid=True), nullable=True),
        schema="ranking",
    )

    op.create_index(
        op.f("ix_tournaments_tournament_competitors_competitor_course_id"),
        "tournament_competitors",
        ["competitor_course_id"],
        unique=False,
        schema="ranking",
    )


def downgrade() -> None:
    """Remove competitor_course_id from tournament_competitors."""

    op.drop_index(
        op.f("ix_tournaments_tournament_competitors_competitor_course_id"),
        table_name="tournament_competitors",
        schema="ranking",
    )

    op.drop_column(
        "tournament_competitors",
        "competitor_course_id",
        schema="ranking",
    )
