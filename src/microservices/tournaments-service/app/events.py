"""
Event handling for Tournaments Service.
Publishes and consumes events via RabbitMQ.
"""

from app.configs.database import get_db_context
from app.configs.logger import logger
from app.formats import FormatRegistry
from app.models import Tournament
from taca_events.pydantic_schemas.matches import (
    MatchCreatedV1,
    MatchDeletedV1,
    MatchResultUpdatedV1,
)
from taca_messaging.rabbitmq_service import RabbitMQService

# Initialize RabbitMQ service for tournaments-service
rabbitmq_service = RabbitMQService(service_name="tournaments-service", logger=logger)


# ==================== Event Handlers ====================
# These handlers respond to events from other services


@rabbitmq_service.event_handler(MatchCreatedV1)
async def handle_match_created(event: MatchCreatedV1):
    """Handle match created event"""
    logger.info(f"Match created event received: match_id={event.data.match_id}")
    tournament_id = event.data.tournament_id

    if not tournament_id:
        logger.warning("Match created event missing tournament_id, cannot process")
        return

    with get_db_context() as db:
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

        if not tournament:
            logger.warning(
                f"Tournament with id {tournament_id} not found for match created event"
            )
            return

        engine = FormatRegistry.get_engine(tournament.format)
        if not engine:
            logger.warning(
                f"No format engine found for tournament format {tournament.format}, cannot process match created event"
            )
            return

        # Route the event to the format engine for processing
        engine.event_handle_match_created(db, event)


@rabbitmq_service.event_handler(MatchDeletedV1)
async def handle_match_deleted(event: MatchDeletedV1):
    """Handle match deleted event"""
    logger.info(f"Match deleted event received: match_id={event.data.match_id}")
    tournament_id = event.data.tournament_id

    if not tournament_id:
        logger.warning("Match deleted event missing tournament_id, cannot process")
        return

    with get_db_context() as db:
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

        if not tournament:
            logger.warning(
                f"Tournament with id {tournament_id} not found for match deleted event"
            )
            return

        engine = FormatRegistry.get_engine(tournament.format)
        if not engine:
            logger.warning(
                f"No format engine found for tournament format {tournament.format}, cannot process match deleted event"
            )
            return

        # Route the event to the format engine for processing
        engine.event_handle_match_deleted(db, event)


@rabbitmq_service.event_handler(MatchResultUpdatedV1)
async def handle_match_result_updated(event: MatchResultUpdatedV1):
    """Handle match result updated event"""
    logger.info(f"Match result updated event received: match_id={event.data.match_id}")
    tournament_id = event.data.tournament_id

    if not tournament_id:
        logger.warning(
            "Match result updated event missing tournament_id, cannot process"
        )
        return

    with get_db_context() as db:
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

        if not tournament:
            logger.warning(
                f"Tournament with id {tournament_id} not found for match result updated event"
            )
            return

        engine = FormatRegistry.get_engine(tournament.format)
        if not engine:
            logger.warning(
                f"No format engine found for tournament format {tournament.format}, cannot process match result updated event"
            )
            return

        # Route the event to the format engine for processing
        engine.event_handle_match_result_updated(db, event)
