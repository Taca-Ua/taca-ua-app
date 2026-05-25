"""init

Revision ID: 96bbb696369b
Revises:
Create Date: 2025-12-01 16:54:37.824893

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS ranking")

    op.create_table(
        "outbox_event",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(255), nullable=False),
        sa.Column("aggregate_type", sa.String(100), nullable=False),
        sa.Column(
            "aggregate_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        schema="ranking",
    )
    op.create_index(
        "ix_ranking_outbox_event_event_type",
        "outbox_event",
        ["event_type"],
        schema="ranking",
    )
    op.create_index(
        "ix_ranking_outbox_event_aggregate_type",
        "outbox_event",
        ["aggregate_type"],
        schema="ranking",
    )
    op.create_index(
        "ix_ranking_outbox_event_aggregate_id",
        "outbox_event",
        ["aggregate_id"],
        schema="ranking",
    )
    op.create_index(
        "ix_ranking_outbox_event_published",
        "outbox_event",
        ["published"],
        schema="ranking",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_ranking_outbox_event_published", table_name="outbox_event", schema="ranking"
    )
    op.drop_index(
        "ix_ranking_outbox_event_aggregate_id",
        table_name="outbox_event",
        schema="ranking",
    )
    op.drop_index(
        "ix_ranking_outbox_event_aggregate_type",
        table_name="outbox_event",
        schema="ranking",
    )
    op.drop_index(
        "ix_ranking_outbox_event_event_type",
        table_name="outbox_event",
        schema="ranking",
    )
    op.drop_table("outbox_event", schema="ranking")
    op.execute("DROP SCHEMA IF EXISTS ranking")
