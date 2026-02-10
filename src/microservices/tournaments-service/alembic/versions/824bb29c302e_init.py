"""init

Revision ID: 824bb29c302e
Revises:
Create Date: 2025-12-06 18:32:34.579287

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "824bb29c302e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create schema if it doesn't exist
    op.execute("CREATE SCHEMA IF NOT EXISTS tournaments")

    # Create tournament table
    op.create_table(
        "tournament",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("modality_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_by", UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="tournaments",
    )
    op.create_index(
        op.f("ix_tournaments_tournament_modality_id"),
        "tournament",
        ["modality_id"],
        unique=False,
        schema="tournaments",
    )
    op.create_index(
        op.f("ix_tournaments_tournament_status"),
        "tournament",
        ["status"],
        unique=False,
        schema="tournaments",
    )

    # Create tournament_ranking_position table
    op.create_table(
        "tournament_ranking_position",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("tournament_id", UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", UUID(as_uuid=True), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tournament_id"],
            ["tournaments.tournament.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tournament_id", "team_id", name="uq_tournament_team"),
        schema="tournaments",
    )
    op.create_index(
        op.f("ix_tournaments_tournament_ranking_position_tournament_id"),
        "tournament_ranking_position",
        ["tournament_id"],
        unique=False,
        schema="tournaments",
    )
    op.create_index(
        op.f("ix_tournaments_tournament_ranking_position_team_id"),
        "tournament_ranking_position",
        ["team_id"],
        unique=False,
        schema="tournaments",
    )

    # Create outbox_event table
    op.create_table(
        "outbox_event",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(255), nullable=False),
        sa.Column("aggregate_type", sa.String(100), nullable=False),
        sa.Column("aggregate_id", UUID(as_uuid=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="tournaments",
    )
    op.create_index(
        op.f("ix_tournaments_outbox_event_event_type"),
        "outbox_event",
        ["event_type"],
        unique=False,
        schema="tournaments",
    )
    op.create_index(
        op.f("ix_tournaments_outbox_event_aggregate_type"),
        "outbox_event",
        ["aggregate_type"],
        unique=False,
        schema="tournaments",
    )
    op.create_index(
        op.f("ix_tournaments_outbox_event_aggregate_id"),
        "outbox_event",
        ["aggregate_id"],
        unique=False,
        schema="tournaments",
    )
    op.create_index(
        op.f("ix_tournaments_outbox_event_published"),
        "outbox_event",
        ["published"],
        unique=False,
        schema="tournaments",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_tournaments_outbox_event_published"),
        table_name="outbox_event",
        schema="tournaments",
    )
    op.drop_index(
        op.f("ix_tournaments_outbox_event_aggregate_id"),
        table_name="outbox_event",
        schema="tournaments",
    )
    op.drop_index(
        op.f("ix_tournaments_outbox_event_aggregate_type"),
        table_name="outbox_event",
        schema="tournaments",
    )
    op.drop_index(
        op.f("ix_tournaments_outbox_event_event_type"),
        table_name="outbox_event",
        schema="tournaments",
    )
    op.drop_table("outbox_event", schema="tournaments")

    op.drop_index(
        op.f("ix_tournaments_tournament_ranking_position_team_id"),
        table_name="tournament_ranking_position",
        schema="tournaments",
    )
    op.drop_index(
        op.f("ix_tournaments_tournament_ranking_position_tournament_id"),
        table_name="tournament_ranking_position",
        schema="tournaments",
    )
    op.drop_table("tournament_ranking_position", schema="tournaments")

    op.drop_index(
        op.f("ix_tournaments_tournament_status"),
        table_name="tournament",
        schema="tournaments",
    )
    op.drop_index(
        op.f("ix_tournaments_tournament_modality_id"),
        table_name="tournament",
        schema="tournaments",
    )
    op.drop_table("tournament", schema="tournaments")
