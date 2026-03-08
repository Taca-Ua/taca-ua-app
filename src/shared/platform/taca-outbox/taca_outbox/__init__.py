"""Shared Outbox Pattern implementation for TACA-UA microservices."""

from .models import create_outbox_model
from .publisher import OutboxPublisher

__all__ = ["create_outbox_model", "OutboxPublisher"]
__version__ = "0.1.0"
