"""add ranking tables

Revision ID: 001
Revises: 000
Create Date: 2026-03-11 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, Sequence[str], None] = "000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "modality_types",
        sa.Column(
            "modality_type_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        schema="ranking",
    )

    op.create_table(
        "modality_type_escaloes",
        sa.Column(
            "_id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "modality_type_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "ranking.modality_types.modality_type_id", ondelete="CASCADE"
            ),
        ),
        sa.Column("min_participants", sa.Integer(), nullable=True),
        sa.Column("max_participants", sa.Integer(), nullable=True),
        sa.Column(
            "points",
            sa.ARRAY(sa.Integer()),
            nullable=False,
        ),
        schema="ranking",
    )

    op.create_table(
        "modalities",
        sa.Column(
            "modality_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "modality_type_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        schema="ranking",
    )
    op.create_index(
        "ix_ranking_modalities_modality_type_id",
        "modalities",
        ["modality_type_id"],
        schema="ranking",
    )

    op.create_table(
        "courses",
        sa.Column(
            "course_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        schema="ranking",
    )

    op.create_table(
        "tournaments",
        sa.Column(
            "tournament_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "modality_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "scoring_format_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "ranking.modality_types.modality_type_id", ondelete="SET NULL"
            ),
        ),
        schema="ranking",
    )
    op.create_index(
        "ix_ranking_tournaments_modality_id",
        "tournaments",
        ["modality_id"],
        schema="ranking",
    )
    op.create_index(
        "ix_ranking_tournaments_scoring_format_id",
        "tournaments",
        ["scoring_format_id"],
        schema="ranking",
    )

    op.create_table(
        "tournament_competitors",
        sa.Column(
            "tournament_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "competitor_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        schema="ranking",
    )
    op.create_index(
        "ix_ranking_tournament_competitors_competitor_id",
        "tournament_competitors",
        ["competitor_id"],
        schema="ranking",
    )

    op.create_table(
        "tournament_results",
        sa.Column(
            "tournament_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "competitor_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        schema="ranking",
    )
    op.create_index(
        "ix_ranking_tournament_results_competitor_id",
        "tournament_results",
        ["competitor_id"],
        schema="ranking",
    )

    op.create_table(
        "general_rankings",
        sa.Column(
            "course_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column("points", sa.Integer(), nullable=False),
        schema="ranking",
    )

    op.create_table(
        "modality_rankings",
        sa.Column(
            "modality_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "course_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column("points", sa.Integer(), nullable=False),
        schema="ranking",
    )
    op.create_index(
        "ix_ranking_modality_rankings_course_id",
        "modality_rankings",
        ["course_id"],
        schema="ranking",
    )

    op.create_table(
        "course_rankings",
        sa.Column(
            "course_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column(
            "modality_breakdown",
            sa.ARRAY(sa.Integer()),
            nullable=False,
        ),
        schema="ranking",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("course_rankings", schema="ranking")
    op.drop_index(
        "ix_ranking_modality_rankings_course_id",
        table_name="modality_rankings",
        schema="ranking",
    )
    op.drop_table("modality_rankings", schema="ranking")
    op.drop_table("general_rankings", schema="ranking")
    op.drop_index(
        "ix_ranking_tournament_results_competitor_id",
        table_name="tournament_results",
        schema="ranking",
    )
    op.drop_table("tournament_results", schema="ranking")
    op.drop_index(
        "ix_ranking_tournament_competitors_competitor_id",
        table_name="tournament_competitors",
        schema="ranking",
    )
    op.drop_table("tournament_competitors", schema="ranking")
    op.drop_index(
        "ix_ranking_tournaments_modality_id",
        table_name="tournaments",
        schema="ranking",
    )
    op.drop_table("tournaments", schema="ranking")
    op.drop_table("courses", schema="ranking")
    op.drop_index(
        "ix_ranking_modalities_modality_type_id",
        table_name="modalities",
        schema="ranking",
    )
    op.drop_table("modalities", schema="ranking")
    op.drop_table("modality_type_escaloes", schema="ranking")
    op.drop_table("modality_types", schema="ranking")
