"""TUA-160: Add general ranking view

Revision ID: c7e4g5f3b2d7
Revises: b5d3f4e2a1c6
Create Date: 2026-03-04 11:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c7e4g5f3b2d7"
down_revision: Union[str, Sequence[str], None] = "b5d3f4e2a1c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add mv_general_ranking materialized view to calculate course rankings
    based on tournament final standings and escalao points configuration.
    """

    # Create general ranking view
    op.create_table(
        "mv_general_ranking",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("course_name", sa.String(), nullable=False),
        sa.Column("course_abbreviation", sa.String(), nullable=False),
        sa.Column("nucleo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nucleo_name", sa.String(), nullable=False),
        sa.Column("nucleo_abbreviation", sa.String(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column(
            "tournaments_participated", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_id", name="uq_general_ranking_course"),
        schema="public_read",
    )

    # Create indexes
    op.create_index(
        "ix_mv_general_ranking_rank",
        "mv_general_ranking",
        ["rank"],
        unique=False,
        schema="public_read",
    )

    op.create_index(
        "ix_mv_general_ranking_course_id",
        "mv_general_ranking",
        ["course_id"],
        unique=False,
        schema="public_read",
    )


def downgrade() -> None:
    """
    Remove general ranking view.
    """

    # Drop indexes
    op.drop_index(
        "ix_mv_general_ranking_course_id",
        table_name="mv_general_ranking",
        schema="public_read",
    )

    op.drop_index(
        "ix_mv_general_ranking_rank",
        table_name="mv_general_ranking",
        schema="public_read",
    )

    # Drop table
    op.drop_table("mv_general_ranking", schema="public_read")
