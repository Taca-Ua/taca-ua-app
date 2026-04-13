"""Add seasons to read model (merge of f0h7j8i6e5g0 and 009)

Revision ID: 010_tua_219_add_seasons
Revises: f0h7j8i6e5g0, 009
Create Date: 2025-01-01 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "010"
down_revision = ("f0h7j8i6e5g0", "009")
branch_labels = None
depends_on = None


def upgrade():
    # Add seasons table
    op.create_table(
        "seasons",
        sa.Column("season_id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("year", name="uq_season_year"),
        schema="public_read",
    )

    # Add season_id to tournaments
    op.add_column(
        "tournaments",
        sa.Column("season_id", sa.UUID(as_uuid=True), nullable=True),
        schema="public_read",
    )

    # Update general_rankings: drop old unique constraint, add season_id, new unique constraint
    op.execute("TRUNCATE TABLE public_read.general_rankings")
    op.execute("TRUNCATE TABLE public_read.modality_rankings")
    op.execute("TRUNCATE TABLE public_read.mv_general_ranking")
    op.execute("TRUNCATE TABLE public_read.mv_modality_rankings")

    op.drop_constraint("uq_general_rankings_course", "general_rankings", schema="public_read")
    op.add_column(
        "general_rankings",
        sa.Column("season_id", sa.UUID(as_uuid=True), nullable=True),
        schema="public_read",
    )
    op.create_unique_constraint(
        "uq_general_rankings_course_season",
        "general_rankings",
        ["course_id", "season_id"],
        schema="public_read",
    )

    # Update modality_rankings
    op.drop_constraint("uq_modality_rankings_modality_course", "modality_rankings", schema="public_read")
    op.add_column(
        "modality_rankings",
        sa.Column("season_id", sa.UUID(as_uuid=True), nullable=True),
        schema="public_read",
    )
    op.create_unique_constraint(
        "uq_modality_rankings_modality_course_season",
        "modality_rankings",
        ["modality_id", "course_id", "season_id"],
        schema="public_read",
    )

    # Update mv_general_ranking
    op.drop_constraint("uq_general_ranking_course", "mv_general_ranking", schema="public_read")
    op.add_column(
        "mv_general_ranking",
        sa.Column("season_id", sa.UUID(as_uuid=True), nullable=True),
        schema="public_read",
    )
    op.create_unique_constraint(
        "uq_general_ranking_course_season",
        "mv_general_ranking",
        ["course_id", "season_id"],
        schema="public_read",
    )

    # Update mv_modality_rankings
    op.drop_constraint("uq_modality_ranking_modality_course", "mv_modality_rankings", schema="public_read")
    op.add_column(
        "mv_modality_rankings",
        sa.Column("season_id", sa.UUID(as_uuid=True), nullable=True),
        schema="public_read",
    )
    op.create_unique_constraint(
        "uq_modality_ranking_modality_course_season",
        "mv_modality_rankings",
        ["modality_id", "course_id", "season_id"],
        schema="public_read",
    )


def downgrade():
    # Revert mv_modality_rankings
    op.drop_constraint("uq_modality_ranking_modality_course_season", "mv_modality_rankings", schema="public_read")
    op.drop_column("mv_modality_rankings", "season_id", schema="public_read")
    op.create_unique_constraint(
        "uq_modality_ranking_modality_course", "mv_modality_rankings",
        ["modality_id", "course_id"], schema="public_read"
    )

    # Revert mv_general_ranking
    op.drop_constraint("uq_general_ranking_course_season", "mv_general_ranking", schema="public_read")
    op.drop_column("mv_general_ranking", "season_id", schema="public_read")
    op.create_unique_constraint(
        "uq_general_ranking_course", "mv_general_ranking", ["course_id"], schema="public_read"
    )

    # Revert modality_rankings
    op.drop_constraint("uq_modality_rankings_modality_course_season", "modality_rankings", schema="public_read")
    op.drop_column("modality_rankings", "season_id", schema="public_read")
    op.create_unique_constraint(
        "uq_modality_rankings_modality_course", "modality_rankings",
        ["modality_id", "course_id"], schema="public_read"
    )

    # Revert general_rankings
    op.drop_constraint("uq_general_rankings_course_season", "general_rankings", schema="public_read")
    op.drop_column("general_rankings", "season_id", schema="public_read")
    op.create_unique_constraint(
        "uq_general_rankings_course", "general_rankings", ["course_id"], schema="public_read"
    )

    # Revert tournaments
    op.drop_column("tournaments", "season_id", schema="public_read")

    # Drop seasons table
    op.drop_table("seasons", schema="public_read")
