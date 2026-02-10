"""
Event handling for Tournaments Service.
Publishes and consumes events via RabbitMQ.
"""

from taca_messaging.rabbitmq_service import RabbitMQService

from .logger import logger

# Initialize RabbitMQ service for tournaments-service
rabbitmq_service = RabbitMQService(service_name="tournaments-service", logger=logger)


# ==================== Event Handlers ====================
# These handlers respond to events from other services


@rabbitmq_service.event_handler("team.created")
async def handle_team_created(data: dict):
    """Handle team created event"""
    logger.info(f"Team created event received: {data}")
    # TODO: Implement business logic if needed


@rabbitmq_service.event_handler("team.deleted")
async def handle_team_deleted(data: dict):
    """Handle team deleted event"""
    logger.info(f"Team deleted event received: {data}")
    # TODO: Remove team from tournaments if needed


@rabbitmq_service.event_handler("modality.deleted")
async def handle_modality_deleted(data: dict):
    """Handle modality deleted event"""
    logger.info(f"Modality deleted event received: {data}")
    # TODO: Handle tournament cleanup if modality is deleted
