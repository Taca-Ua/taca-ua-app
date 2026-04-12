"""Add season_id to ranking derived tables

Revision ID: 003_tua_219_add_season_id
Revises: 002
Create Date: 2025-01-01 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    # Truncate derived tables first (data will be recomputed by event replay)
    op.execute("TRUNCATE TABLE ranking.general_rankings")
    op.execute("TRUNCATE TABLE ranking.course_rankings")
    op.execute("TRUNCATE TABLE ranking.modality_rankings")

    # Add season_id to Tournament
    op.add_column(
        "tournaments",
        sa.Column("season_id", sa.UUID(as_uuid=True), nullable=True),
        schema="ranking",
    )

    # Restructure general_rankings: drop old PK, add surrogate PK + season_id
    op.drop_constraint(
        "general_rankings_pkey", "general_rankings", schema="ranking", type_="primary"
    )
    op.add_column(
        "general_rankings",
        sa.Column(
            "_id",
            sa.Integer(),
            sa.Identity(always=True),
            nullable=False,
        ),
        schema="ranking",
    )
    op.add_column(
        "general_rankings",
        sa.Column("season_id", sa.UUID(as_uuid=True), nullable=True),
        schema="ranking",
    )
    op.create_primary_key("general_rankings_pkey", "general_rankings", ["_id"], schema="ranking")
    op.create_unique_constraint(
        "uq_general_rankings_course_season",
        "general_rankings",
        ["course_id", "season_id"],
        schema="ranking",
    )

    # Restructure modality_rankings
    op.drop_constraint(
        "modality_rankings_pkey", "modality_rankings", schema="ranking", type_="primary"
    )
    op.add_column(
        "modality_rankings",
        sa.Column(
            "_id",
            sa.Integer(),
            sa.Identity(always=True),
            nullable=False,
        ),
        schema="ranking",
    )
    op.add_column(
        "modality_rankings",
        sa.Column("season_id", sa.UUID(as_uuid=True), nullable=True),
        schema="ranking",
    )
    op.create_primary_key("modality_rankings_pkey", "modality_rankings", ["_id"], schema="ranking")
    op.create_unique_constraint(
        "uq_modality_rankings_modality_course_season",
        "modality_rankings",
        ["modality_id", "course_id", "season_id"],
        schema="ranking",
    )

    # Restructure course_rankings
    op.drop_constraint(
        "course_rankings_pkey", "course_rankings", schema="ranking", type_="primary"
    )
    op.add_column(
        "course_rankings",
        sa.Column(
            "_id",
            sa.Integer(),
            sa.Identity(always=True),
            nullable=False,
        ),
        schema="ranking",
    )
    op.add_column(
        "course_rankings",
        sa.Column("season_id", sa.UUID(as_uuid=True), nullable=True),
        schema="ranking",
    )
    op.create_primary_key("course_rankings_pkey", "course_rankings", ["_id"], schema="ranking")
    op.create_unique_constraint(
        "uq_course_rankings_course_season",
        "course_rankings",
        ["course_id", "season_id"],
        schema="ranking",
    )


def downgrade():
    # Remove season_id from tournaments
    op.drop_column("tournaments", "season_id", schema="ranking")

    # Revert general_rankings
    op.drop_constraint("uq_general_rankings_course_season", "general_rankings", schema="ranking")
    op.drop_constraint("general_rankings_pkey", "general_rankings", schema="ranking", type_="primary")
    op.drop_column("general_rankings", "_id", schema="ranking")
    op.drop_column("general_rankings", "season_id", schema="ranking")
    op.create_primary_key("general_rankings_pkey", "general_rankings", ["course_id"], schema="ranking")

    # Revert modality_rankings
    op.drop_constraint("uq_modality_rankings_modality_course_season", "modality_rankings", schema="ranking")
    op.drop_constraint("modality_rankings_pkey", "modality_rankings", schema="ranking", type_="primary")
    op.drop_column("modality_rankings", "_id", schema="ranking")
    op.drop_column("modality_rankings", "season_id", schema="ranking")
    op.create_primary_key("modality_rankings_pkey", "modality_rankings", ["modality_id", "course_id"], schema="ranking")

    # Revert course_rankings
    op.drop_constraint("uq_course_rankings_course_season", "course_rankings", schema="ranking")
    op.drop_constraint("course_rankings_pkey", "course_rankings", schema="ranking", type_="primary")
    op.drop_column("course_rankings", "_id", schema="ranking")
    op.drop_column("course_rankings", "season_id", schema="ranking")
    op.create_primary_key("course_rankings_pkey", "course_rankings", ["course_id"], schema="ranking")
