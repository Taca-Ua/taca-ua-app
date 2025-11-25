"""RabbitMQ messaging utilities for TACA-UA microservices."""

from .rabbitmq_service import RabbitMQService, event_handler, rabbitmq_service

__all__ = ["RabbitMQService", "rabbitmq_service", "event_handler"]
__version__ = "0.1.0"
