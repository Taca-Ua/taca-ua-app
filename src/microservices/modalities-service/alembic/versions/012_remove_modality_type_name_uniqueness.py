"""remove modality type name uniqueness

Revision ID: 012
Revises: 011
Create Date: 2026-04-30 01:06:34.656139

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "012"
down_revision: Union[str, Sequence[str], None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "modality_type_name_key", "modality_type", schema="modalities", type_="unique"
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.create_unique_constraint(
        "modality_type_name_key", "modality_type", ["name"], schema="modalities"
    )
    pass
