"""Add modality_rankins materialized view

Revision ID: 007
Revises: 006
Create Date: 2026-03-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, Sequence[str], None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create mv_modality_rankings materialized view
    op.create_table(
        "mv_modality_rankings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("modality_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_name", sa.String(), nullable=True),
        sa.Column("course_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("course_name", sa.String(), nullable=False),
        sa.Column("course_abbreviation", sa.String(), nullable=False),
        sa.Column("nucleo_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("nucleo_name", sa.String(), nullable=False),
        sa.Column("nucleo_abbreviation", sa.String(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, default=0),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "modality_id", "course_id", name="uq_modality_ranking_modality_course"
        ),
        schema="public_read",
    )
    op.create_index(
        "ix_mv_modality_rankings_rank",
        "mv_modality_rankings",
        ["modality_id", "rank"],
        schema="public_read",
    )
    op.create_index(
        "ix_mv_modality_rankings_course_id",
        "mv_modality_rankings",
        ["modality_id", "course_id"],
        schema="public_read",
    )


def downgrade() -> None:
    # Drop mv_modality_rankings materialized view
    op.drop_index(
        "ix_mv_modality_rankings_rank",
        table_name="mv_modality_rankings",
        schema="public_read",
    )
    op.drop_index(
        "ix_mv_modality_rankings_course_id",
        table_name="mv_modality_rankings",
        schema="public_read",
    )
    op.drop_table("mv_modality_rankings", schema="public_read")
