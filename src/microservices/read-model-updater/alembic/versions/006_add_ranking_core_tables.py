"""Add ranking core tables

Revision ID: 006
Revises: d8f5h6g4c3e8
Create Date: 2026-03-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, Sequence[str], None] = "d8f5h6g4c3e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create general_rankings table
    op.create_table(
        "general_rankings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("course_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "tournaments_participated", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.UniqueConstraint("course_id", name="uq_general_rankings_course"),
        sa.Index("ix_general_rankings_course_id", "course_id"),
        schema="public_read",
    )

    # Create modality_rankings table
    op.create_table(
        "modality_rankings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("modality_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("course_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint(
            "modality_id", "course_id", name="uq_modality_rankings_modality_course"
        ),
        sa.Index("ix_modality_rankings_modality_id", "modality_id"),
        sa.Index("ix_modality_rankings_course_id", "course_id"),
        schema="public_read",
    )


def downgrade() -> None:
    op.drop_table("modality_rankings", schema="public_read")
    op.drop_table("general_rankings", schema="public_read")
