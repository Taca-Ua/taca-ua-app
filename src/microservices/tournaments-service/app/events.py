"""
Event handling for Tournaments Service.
Publishes and consumes events via RabbitMQ.
"""

from taca_events import EventRegistry, ModalityDeletedV1, TeamCreatedV1, TeamDeletedV1
from taca_messaging.rabbitmq_service import RabbitMQService

from .logger import logger

# Initialize RabbitMQ service for tournaments-service
rabbitmq_service = RabbitMQService(service_name="tournaments-service", logger=logger)


# ==================== Event Handlers ====================
# These handlers respond to events from other services


@rabbitmq_service.event_handler("team.created")
async def handle_team_created(raw_event: dict):
    """Handle team created event"""
    event = EventRegistry.parse("team.created", raw_event)
    if not isinstance(event, TeamCreatedV1):
        return
    logger.info(f"Team created event received: team_id={event.data.team_id}")
    # TODO: Implement business logic if needed


@rabbitmq_service.event_handler("team.deleted")
async def handle_team_deleted(raw_event: dict):
    """Handle team deleted event"""
    event = EventRegistry.parse("team.deleted", raw_event)
    if not isinstance(event, TeamDeletedV1):
        return
    logger.info(f"Team deleted event received: team_id={event.data.team_id}")
    # TODO: Remove team from tournaments if needed


@rabbitmq_service.event_handler("modality.deleted")
async def handle_modality_deleted(raw_event: dict):
    """Handle modality deleted event"""
    event = EventRegistry.parse("modality.deleted", raw_event)
    if not isinstance(event, ModalityDeletedV1):
        return
    logger.info(
        f"Modality deleted event received: modality_id={event.data.modality_id}"
    )
    # TODO: Handle tournament cleanup if modality is deleted
