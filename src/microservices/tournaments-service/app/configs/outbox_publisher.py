"""
Outbox Publisher – tournaments-service

Wires the shared OutboxPublisher from taca_outbox to this service’s specific
dependencies (ORM model, session factory, RabbitMQ service, logger).
"""

from app.models import OutboxEvent
from taca_messaging import RabbitMQService
from taca_outbox import OutboxPublisher

from .database import SessionLocal
from .logger import logger

# Initialize RabbitMQ service for tournaments-service
rabbitmq_service = RabbitMQService(service_name="tournaments-service", logger=logger)


# Singleton instance used by main.py (lifespan) and event_helpers.py
outbox_publisher = OutboxPublisher(
    outbox_model=OutboxEvent,
    session_factory=SessionLocal,
    rabbitmq_service=rabbitmq_service,
    logger=logger,
    service_name="tournaments-service",
)
