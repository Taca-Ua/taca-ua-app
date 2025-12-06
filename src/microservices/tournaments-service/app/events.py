"""
Event handling for Tournaments Service.
Publishes and consumes events via RabbitMQ.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID

from taca_messaging import RabbitMQService

from .logger import logger
from .models import Tournament

# This will be injected from main.py
rabbitmq_service = RabbitMQService(service_name="tournaments-service")


# Event Publishers
async def publish_tournament_created(tournament: Tournament):
    """Publish TournamentCreated event."""
    if not rabbitmq_service:
        logger.warning("RabbitMQ service not initialized")
        return

    event_data = {
        "tournament_id": str(tournament.id),
        "modality_id": str(tournament.modality_id),
        "season_id": str(tournament.season_id),
        "name": tournament.name,
        "created_at": tournament.created_at.isoformat(),
    }

    await rabbitmq_service.publish_event("tournament.created", event_data)
    logger.info(f"Published tournament.created event for tournament {tournament.id}")


async def publish_tournament_updated(tournament: Tournament, changes: Dict[str, Any]):
    """Publish TournamentUpdated event."""
    if not rabbitmq_service:
        logger.warning("RabbitMQ service not initialized")
        return

    event_data = {
        "tournament_id": str(tournament.id),
        "changes": changes,
        "updated_at": (
            tournament.updated_at.isoformat() if tournament.updated_at else None
        ),
    }

    await rabbitmq_service.publish_event("tournament.updated", event_data)
    logger.info(f"Published tournament.updated event for tournament {tournament.id}")


async def publish_tournament_finished(tournament: Tournament):
    """Publish TournamentFinished event."""
    if not rabbitmq_service:
        logger.warning("RabbitMQ service not initialized")
        return

    event_data = {
        "tournament_id": str(tournament.id),
        "modality_id": str(tournament.modality_id),
        "season_id": str(tournament.season_id),
        "finished_at": (
            tournament.finished_at.isoformat() if tournament.finished_at else None
        ),
    }

    await rabbitmq_service.publish_event("tournament.finished", event_data)
    logger.info(f"Published tournament.finished event for tournament {tournament.id}")


async def publish_tournament_deleted(tournament_id: UUID):
    """Publish TournamentDeleted event."""
    if not rabbitmq_service:
        logger.warning("RabbitMQ service not initialized")
        return

    event_data = {
        "tournament_id": str(tournament_id),
        "deleted_at": datetime.now(timezone.utc).isoformat(),
    }

    await rabbitmq_service.publish_event("tournament.deleted", event_data)
    logger.info(f"Published tournament.deleted event for tournament {tournament_id}")


# Event Consumers
@rabbitmq_service.event_handler("modality.deleted")
async def handle_modality_deleted(data: dict):
    """
    Consumes: modality.deleted

    Handle ModalityDeleted event.
    Marks all tournaments of this modality as invalid or cancels them.
    """
    modality_id = data.get("modality_id")
    logger.info(f"Handling modality.deleted event for modality {modality_id}")

    # Implementation to be added when database operations are needed
    # - Find all tournaments with this modality_id
    # - Mark them as cancelled or invalid
    # - Publish events if needed
    logger.warning("ModalityDeleted handler not fully implemented yet")


@rabbitmq_service.event_handler("season.finished")
async def handle_season_finished(data: dict):
    """
    Consumes: season.finished

    Handle SeasonFinished event.
    Finalizes automatically all open tournaments of this season.
    """
    season_id = data.get("season_id")
    logger.info(f"Handling season.finished event for season {season_id}")

    # Implementation to be added when database operations are needed
    # - Find all tournaments with this season_id that are not finished
    # - Mark them as finished
    # - Publish tournament.finished events
    logger.warning("SeasonFinished handler not fully implemented yet")
