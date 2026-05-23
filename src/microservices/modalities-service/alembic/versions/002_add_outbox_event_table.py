"""Add outbox event table

Revision ID: 002
Revises: 001
Create Date: 2025-12-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create outbox_event table
    op.create_table(
        "outbox_event",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=255), nullable=False),
        sa.Column("aggregate_type", sa.String(length=100), nullable=False),
        sa.Column("aggregate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="modalities",
    )
    op.create_index(
        op.f("ix_outbox_event_event_type"),
        "outbox_event",
        ["event_type"],
        unique=False,
        schema="modalities",
    )
    op.create_index(
        op.f("ix_outbox_event_aggregate_type"),
        "outbox_event",
        ["aggregate_type"],
        unique=False,
        schema="modalities",
    )
    op.create_index(
        op.f("ix_outbox_event_aggregate_id"),
        "outbox_event",
        ["aggregate_id"],
        unique=False,
        schema="modalities",
    )
    op.create_index(
        op.f("ix_outbox_event_published"),
        "outbox_event",
        ["published"],
        unique=False,
        schema="modalities",
    )

    # Create composite index for efficient querying of unpublished events
    op.create_index(
        "ix_outbox_event_published_created",
        "outbox_event",
        ["published", "created_at"],
        unique=False,
        schema="modalities",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_outbox_event_published_created",
        table_name="outbox_event",
        schema="modalities",
    )
    op.drop_index(
        op.f("ix_outbox_event_published"),
        table_name="outbox_event",
        schema="modalities",
    )
    op.drop_index(
        op.f("ix_outbox_event_aggregate_id"),
        table_name="outbox_event",
        schema="modalities",
    )
    op.drop_index(
        op.f("ix_outbox_event_aggregate_type"),
        table_name="outbox_event",
        schema="modalities",
    )
    op.drop_index(
        op.f("ix_outbox_event_event_type"),
        table_name="outbox_event",
        schema="modalities",
    )
    op.drop_table("outbox_event", schema="modalities")
