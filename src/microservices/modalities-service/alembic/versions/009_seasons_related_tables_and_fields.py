"""seasons related tables and fields

Revision ID: 009
Revises: 008
Create Date: 2026-04-29 15:22:25.415990

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: Union[str, Sequence[str], None] = "008"
branch_labels: Union[str, Sequence[str], None] = ("seasons",)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create new tables
    op.create_table(
        "season",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_by", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("finished_by", sa.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="modalities",
    )
    op.execute(  # Insert default season
        sa.text(
            "INSERT INTO modalities.season (id, name, created_by) VALUES (1, 'Default Season', '00000000-0000-0000-0000-000000000000')"
        )
    )

    op.create_table(
        "season_course",
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["course_id"], ["modalities.course.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["season_id"], ["modalities.season.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("season_id", "course_id"),
        schema="modalities",
    )
    op.bulk_insert(  # Insert current courses into season_course for default season
        sa.table(
            "season_course",
            sa.column("season_id", sa.Integer()),
            sa.column("course_id", sa.UUID(as_uuid=True)),
            schema="modalities",
        ),
        [
            {"season_id": 1, "course_id": row[0]}
            for row in op.get_bind()
            .execute(sa.text("SELECT id FROM modalities.course"))
            .fetchall()
        ],
    )

    op.create_table(
        "season_modality",
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("modality_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_type_id", sa.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["modality_id"], ["modalities.modality.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["modality_type_id"], ["modalities.modality_type.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["season_id"], ["modalities.season.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("season_id", "modality_id"),
        schema="modalities",
    )
    op.bulk_insert(  # Insert default season-modality associations
        sa.table(
            "season_modality",
            sa.column("season_id", sa.Integer()),
            sa.column("modality_id", sa.UUID(as_uuid=True)),
            sa.column("modality_type_id", sa.UUID(as_uuid=True)),
            schema="modalities",
        ),
        [
            {"season_id": 1, "modality_id": row[0], "modality_type_id": row[1]}
            for row in op.get_bind()
            .execute(sa.text("SELECT id, modality_type_id FROM modalities.modality"))
            .fetchall()
        ],
    )

    # Update modality_type table to include season_id
    op.add_column(
        "modality_type",
        sa.Column("season_id", sa.Integer(), nullable=True),
        schema="modalities",
    )
    op.create_foreign_key(
        "fk_modality_type_season",
        "modality_type",
        "season",
        ["season_id"],
        ["id"],
        ondelete="CASCADE",
        source_schema="modalities",
        referent_schema="modalities",
    )
    op.execute(  # Set season_id for existing modality types to default season
        sa.text("UPDATE modalities.modality_type SET season_id = 1")
    )

    # Update modality table to lose modality_type_id
    op.drop_constraint(
        "modality_modality_type_id_fkey",
        "modality",
        schema="modalities",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_modality_modality_type_id", table_name="modality", schema="modalities"
    )
    op.drop_column("modality", "modality_type_id", schema="modalities")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "modality",
        sa.Column("modality_type_id", sa.UUID(as_uuid=True), nullable=True),
        schema="modalities",
    )
    op.create_foreign_key(
        "modality_modality_type_id_fkey",
        "modality",
        "modality_type",
        ["modality_type_id"],
        ["id"],
        ondelete="CASCADE",
        schema="modalities",
    )
    op.create_index(
        "ix_modality_modality_type_id",
        "modality",
        ["modality_type_id"],
        schema="modalities",
    )
    op.drop_constraint(
        "fk_modality_type_season",
        "modality_type",
        schema="modalities",
        type_="foreignkey",
    )
    op.drop_column("modality_type", "season_id", schema="modalities")
    op.drop_table("season_modality", schema="modalities")
    op.drop_table("season_course", schema="modalities")
    op.drop_table("season", schema="modalities")
    pass
