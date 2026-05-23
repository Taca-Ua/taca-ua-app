"""RabbitMQ messaging utilities for TACA-UA microservices."""

from .rabbitmq_service import PausableRabbitMQService, RabbitMQService

__all__ = ["RabbitMQService", "PausableRabbitMQService"]
__version__ = "0.1.0"
