"""lineup player is pk

Revision ID: 003
Revises: 002
Create Date: 2026-04-01 17:11:36.800403

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, Sequence[str], None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Drop the existing composite PK constraint
    op.drop_constraint("pk_lineup", "lineup", schema="matches", type_="primary")

    # 2. Recreate it with player_id included
    op.create_primary_key(
        "pk_lineup",
        "lineup",
        ["match_id", "participant", "player_id"],
        schema="matches",
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Drop the new 3-column PK
    op.drop_constraint("pk_lineup", "lineup", schema="matches", type_="primary")

    # 2. WARNING: this will fail if duplicate (match_id, participant) rows exist
    op.create_primary_key(
        "pk_lineup",
        "lineup",
        ["match_id", "participant"],
        schema="matches",
    )
