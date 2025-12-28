"""add_course_table

Revision ID: 2c31649e9981
Revises: 1b21539d9870
Create Date: 2025-12-08 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2c31649e9981"
down_revision: Union[str, Sequence[str], None] = "1b21539d9870"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create course table
    op.create_table(
        "course",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("abbreviation", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="modalities",
    )

    # Create unique index on abbreviation
    op.create_index(
        op.f("ix_modalities_course_abbreviation"),
        "course",
        ["abbreviation"],
        unique=True,
        schema="modalities",
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index
    op.drop_index(
        op.f("ix_modalities_course_abbreviation"),
        table_name="course",
        schema="modalities",
    )

    # Drop table
    op.drop_table("course", schema="modalities")
