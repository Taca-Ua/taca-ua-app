"""add season_id across tables

Revision ID: 004
Revises: 003
Create Date: 2026-05-10 20:06:25.760809

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, Sequence[str], None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade_single_table(table_name: str, old_primary_key: list) -> None:
    """Upgrade a single table by adding season_id."""
    op.add_column(
        table_name,
        sa.Column("season_id", sa.Integer(), nullable=True),
        schema="ranking",
    )
    op.execute(f"UPDATE ranking.{table_name} SET season_id = 0")
    op.execute(f"ALTER TABLE ranking.{table_name} DROP CONSTRAINT {table_name}_pkey")
    new_primary_key = ["season_id"] + old_primary_key
    op.create_primary_key(
        f"{table_name}_pkey", table_name, new_primary_key, schema="ranking"
    )
    op.alter_column(table_name, "season_id", nullable=False, schema="ranking")


def downgrade_single_table(table_name: str, old_primary_key: list) -> None:
    """Downgrade a single table by removing season_id."""
    op.drop_constraint(f"{table_name}_pkey", table_name, schema="ranking")
    op.create_primary_key(
        f"{table_name}_pkey", table_name, old_primary_key, schema="ranking"
    )
    op.drop_column("season_id", table_name, schema="ranking")


def upgrade() -> None:
    """Upgrade schema."""
    upgrade_single_table("tournaments", ["tournament_id"])
    upgrade_single_table("general_rankings", ["course_id"])
    upgrade_single_table("modality_rankings", ["modality_id", "course_id"])
    upgrade_single_table("course_rankings", ["course_id"])


def downgrade() -> None:
    """Downgrade schema."""
    downgrade_single_table("course_rankings", ["course_id"])
    downgrade_single_table("modality_rankings", ["modality_id", "course_id"])
    downgrade_single_table("general_rankings", ["course_id"])
    downgrade_single_table("tournaments", ["tournament_id"])
