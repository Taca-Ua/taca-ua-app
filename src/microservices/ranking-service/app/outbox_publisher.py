"""
Outbox Publisher — ranking-service

Wires the shared OutboxPublisher from taca_outbox to this service's specific
dependencies (ORM model, session factory, RabbitMQ service, logger).

A dedicated RabbitMQ connection is used for publishing so the outbox
publisher remains independent of the consumer connection in events.py.
"""

from taca_messaging import PausableRabbitMQService
from taca_outbox import OutboxPublisher

from .database import SessionLocal
from .logger import logger
from .models import OutboxEvent

# Separate RabbitMQ service used exclusively for publishing outbox events.
# Avoids circular import with events.py (which owns the consumer service).
_publishing_rabbitmq = PausableRabbitMQService(service_name="ranking-service")

# Singleton instance used by main.py (lifespan) and ranking_processor.py
outbox_publisher = OutboxPublisher(
    outbox_model=OutboxEvent,
    session_factory=SessionLocal,
    rabbitmq_service=_publishing_rabbitmq,
    logger=logger,
    service_name="ranking-service",
)
