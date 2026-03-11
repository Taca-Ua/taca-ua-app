"""
Event handling for Tournaments Service.
Publishes and consumes events via RabbitMQ.
"""

from taca_events.pydantic_schemas.modalities import (
    ModalityDeletedV1,
    TeamCreatedV1,
    TeamDeletedV1,
)
from taca_messaging.rabbitmq_service import RabbitMQService

from .logger import logger

# Initialize RabbitMQ service for tournaments-service
rabbitmq_service = RabbitMQService(service_name="tournaments-service", logger=logger)


# ==================== Event Handlers ====================
# These handlers respond to events from other services


@rabbitmq_service.event_handler(TeamCreatedV1)
async def handle_team_created(event: TeamCreatedV1):
    """Handle team created event"""
    logger.info(f"Team created event received: team_id={event.data.team_id}")
    # TODO: Implement business logic if needed


@rabbitmq_service.event_handler(TeamDeletedV1)
async def handle_team_deleted(event: TeamDeletedV1):
    """Handle team deleted event"""
    logger.info(f"Team deleted event received: team_id={event.data.team_id}")
    # TODO: Remove team from tournaments if needed


@rabbitmq_service.event_handler(ModalityDeletedV1)
async def handle_modality_deleted(event: ModalityDeletedV1):
    """Handle modality deleted event"""
    logger.info(
        f"Modality deleted event received: modality_id={event.data.modality_id}"
    )
    # TODO: Handle tournament cleanup if modality is deleted
