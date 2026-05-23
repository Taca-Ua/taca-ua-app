"""
Factory function for creating the OutboxEvent SQLAlchemy model with a
configurable schema.  Each microservice calls this once with its own schema
name so the database structure (schema.outbox_event) remains unchanged.

Usage::

    from taca_outbox.models import create_outbox_model

    OutboxEvent = create_outbox_model(Base, schema="ranking")
"""

import uuid
from datetime import datetime, timezone
from typing import Type

import sqlalchemy as sa
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeMeta


def create_outbox_model(Base: DeclarativeMeta, schema: str) -> Type:
    """
    Return a new OutboxEvent ORM class bound to *Base* and the given *schema*.

    Parameters
    ----------
    Base:
        The ``declarative_base()`` instance belonging to the calling service.
    schema:
        PostgreSQL schema name (e.g. ``"ranking"``, ``"matches"``).

    Returns
    -------
    OutboxEvent class mapped to ``<schema>.outbox_event``.
    """

    class OutboxEvent(Base):  # type: ignore[valid-type,misc]
        """
        Outbox pattern for reliable event publishing.
        Events are stored here first, then published by the OutboxPublisher.
        """

        __tablename__ = "outbox_event"
        __table_args__ = {"schema": schema}

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        event_type = Column(String(255), nullable=False, index=True)
        aggregate_type = Column(String(100), nullable=False, index=True)
        aggregate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
        payload = Column(sa.JSON, nullable=False)
        published = Column(Boolean, default=False, nullable=False, index=True)
        published_at = Column(DateTime(timezone=True), nullable=True)
        created_at = Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
        retry_count = Column(Integer, default=0, nullable=False)
        last_error = Column(Text, nullable=True)

        def to_dict(self):
            return {
                "id": str(self.id),
                "event_type": self.event_type,
                "aggregate_type": self.aggregate_type,
                "aggregate_id": str(self.aggregate_id),
                "payload": self.payload,
                "published": self.published,
                "published_at": (
                    self.published_at.isoformat() if self.published_at else None
                ),
                "created_at": (
                    self.created_at.isoformat() if self.created_at else None
                ),
                "retry_count": self.retry_count,
                "last_error": self.last_error,
            }

        def __repr__(self) -> str:
            return (
                f"<OutboxEvent id={self.id} event_type={self.event_type!r} "
                f"published={self.published}>"
            )

    # Give the class a unique __name__ so SQLAlchemy's registry does not
    # complain when the same Base is shared across multiple calls.
    OutboxEvent.__name__ = f"OutboxEvent_{schema}"
    OutboxEvent.__qualname__ = f"OutboxEvent_{schema}"

    return OutboxEvent
