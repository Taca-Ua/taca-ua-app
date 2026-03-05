"""
Outbox Publisher – matches-service

Wires the shared OutboxPublisher from taca_outbox to this service’s specific
dependencies (ORM model, session factory, RabbitMQ service, logger).
"""

from taca_outbox import OutboxPublisher as _OutboxPublisher

from .database import SessionLocal
from .events import rabbitmq_service
from .logger import logger
from .models import OutboxEvent

# Singleton instance used by main.py (lifespan) and event_helpers.py
outbox_publisher = _OutboxPublisher(
    outbox_model=OutboxEvent,
    session_factory=SessionLocal,
    rabbitmq_service=rabbitmq_service,
    logger=logger,
)
