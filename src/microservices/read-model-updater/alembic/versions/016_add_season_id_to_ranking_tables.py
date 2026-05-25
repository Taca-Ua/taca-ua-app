"""add season_id to ranking tables

Revision ID: 016
Revises: 015
Create Date: 2026-05-12 20:27:15.282404

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "016"
down_revision: Union[str, Sequence[str], None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "general_rankings",
        sa.Column(
            "season_id", sa.Integer(), nullable=True, server_default=sa.text("1")
        ),
        schema="public_read",
    )
    op.add_column(
        "modality_rankings",
        sa.Column(
            "season_id", sa.Integer(), nullable=True, server_default=sa.text("1")
        ),
        schema="public_read",
    )
    op.add_column(
        "mv_general_ranking",
        sa.Column(
            "season_id", sa.Integer(), nullable=True, server_default=sa.text("1")
        ),
        schema="public_read",
    )
    op.add_column(
        "mv_modality_rankings",
        sa.Column(
            "season_id", sa.Integer(), nullable=True, server_default=sa.text("1")
        ),
        schema="public_read",
    )

    op.drop_constraint(
        "uq_general_rankings_course",
        "general_rankings",
        type_="unique",
        schema="public_read",
    )
    op.create_unique_constraint(
        "uq_general_rankings_course_season",
        "general_rankings",
        ["course_id", "season_id"],
        schema="public_read",
    )

    op.drop_constraint(
        "uq_modality_rankings_modality_course",
        "modality_rankings",
        type_="unique",
        schema="public_read",
    )
    op.create_unique_constraint(
        "uq_modality_rankings_course_modality_season",
        "modality_rankings",
        ["course_id", "modality_id", "season_id"],
        schema="public_read",
    )

    op.drop_constraint(
        "uq_general_ranking_course",
        "mv_general_ranking",
        type_="unique",
        schema="public_read",
    )
    op.create_unique_constraint(
        "uq_mv_general_ranking_course_season",
        "mv_general_ranking",
        ["course_id", "season_id"],
        schema="public_read",
    )

    op.drop_constraint(
        "uq_modality_ranking_modality_course",
        "mv_modality_rankings",
        type_="unique",
        schema="public_read",
    )
    op.create_unique_constraint(
        "uq_mv_modality_ranking_modality_course_season",
        "mv_modality_rankings",
        ["modality_id", "course_id", "season_id"],
        schema="public_read",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "uq_general_rankings_course_season",
        "general_rankings",
        type_="unique",
        schema="public_read",
    )
    op.create_unique_constraint(
        "uq_general_rankings_course",
        "general_rankings",
        ["course_id"],
        schema="public_read",
    )

    op.drop_constraint(
        "uq_modality_rankings_course_modality_season",
        "modality_rankings",
        type_="unique",
        schema="public_read",
    )
    op.create_unique_constraint(
        "uq_modality_rankings_course_modality",
        "modality_rankings",
        ["course_id", "modality_id"],
        schema="public_read",
    )

    op.drop_constraint(
        "uq_mv_general_ranking_course_season",
        "mv_general_ranking",
        type_="unique",
        schema="public_read",
    )
    op.create_unique_constraint(
        "uq_general_ranking_course",
        "mv_general_ranking",
        ["course_id"],
        schema="public_read",
    )

    op.drop_constraint(
        "uq_mv_modality_ranking_modality_course_season",
        "mv_modality_rankings",
        type_="unique",
        schema="public_read",
    )
    op.create_unique_constraint(
        "uq_modality_ranking_modality_course",
        "mv_modality_rankings",
        ["modality_id", "course_id"],
        schema="public_read",
    )

    op.drop_column("general_rankings", "season_id", schema="public_read")
    op.drop_column("modality_rankings", "season_id", schema="public_read")
    op.drop_column("mv_general_ranking", "season_id", schema="public_read")
    op.drop_column("mv_modality_rankings", "season_id", schema="public_read")
