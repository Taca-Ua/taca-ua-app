"""
Event handling for read-model-updater.
Publishes and consumes events via RabbitMQ.
"""

from typing import Any, Dict

from taca_events import RoutingKeys
from taca_messaging.rabbitmq_service import RabbitMQService

from .logger import logger

# Initialize RabbitMQ service for read-model-updater
rabbitmq_service = RabbitMQService(service_name="read-model-updater", logger=logger)


# ==================== Event Handlers ====================
# These handlers respond to events from other services


# ==================== Nucleo Events ====================


@rabbitmq_service.event_handler(RoutingKeys.NUCLEO_CREATED)
def handle_nucleo_created(event_data: Dict[str, Any]):
    """
    Handle nucleo created event.

    Event data schema:
    {
        "nucleo_id": str (UUID),
        "name": str,
        "abbreviation": str,
        "created_at": str (ISO datetime)
    }
    """
    logger.info(
        "event_received",
        event_type="nucleo.created",
        nucleo_id=event_data.get("nucleo_id"),
    )

    # Note: Currently no nucleo-specific read model views to update
    # This handler is a placeholder for future nucleo-related views
    # The nucleo data is already stored in the modalities schema

    logger.debug(
        "nucleo_created_processed",
        nucleo_id=event_data.get("nucleo_id"),
        name=event_data.get("name"),
    )


@rabbitmq_service.event_handler(RoutingKeys.NUCLEO_UPDATED)
def handle_nucleo_updated(event_data: Dict[str, Any]):
    """
    Handle nucleo updated event.

    Event data schema:
    {
        "nucleo_id": str (UUID),
        "changes": dict,
        "updated_at": str (ISO datetime)
    }

    Note: The actual event from nucleo_routes.py sends the full nucleo dict,
    not just changes. We handle both formats.
    """
    nucleo_id = event_data.get("nucleo_id") or event_data.get("id")

    logger.info("event_received", event_type="nucleo.updated", nucleo_id=nucleo_id)

    # Note: Currently no nucleo-specific read model views to update
    # This handler is a placeholder for future nucleo-related views
    # If we had views that include nucleo name/abbreviation, we would:
    # 1. Query all affected records
    # 2. Update them with new nucleo data

    logger.debug(
        "nucleo_updated_processed",
        nucleo_id=nucleo_id,
        changes=event_data.get("changes") or "full_update",
    )


@rabbitmq_service.event_handler(RoutingKeys.NUCLEO_DELETED)
def handle_nucleo_deleted(event_data: Dict[str, Any]):
    """
    Handle nucleo deleted event.

    Event data schema:
    {
        "nucleo_id": str (UUID),
        "deleted_at": str (ISO datetime)
    }
    """
    logger.info(
        "event_received",
        event_type="nucleo.deleted",
        nucleo_id=event_data.get("nucleo_id"),
    )

    # Note: Currently no nucleo-specific read model views to update
    # This handler is a placeholder for future nucleo-related views
    # If we had views that reference nucleos, we would:
    # 1. Delete or mark as deleted all related records
    # 2. Handle cascading updates appropriately

    logger.debug("nucleo_deleted_processed", nucleo_id=event_data.get("nucleo_id"))


@rabbitmq_service.event_handler("#")
def handle_all_events(event_data: Dict[str, Any]):
    """
    Catch-all handler for all events.

    This can be used for logging or monitoring purposes.
    """
    logger.info("event_caught_in_catch_all", event_data=event_data)
