"""
Event handling for Matches Service.
"""

from app.database import get_db
from app.logger import logger
from app.models import Match
from taca_events.pydantic_schemas.tournaments import TournamentDeletedV1
from taca_messaging import RabbitMQService

rabbitmq_service = RabbitMQService(service_name="matches-service")


@rabbitmq_service.event_handler(TournamentDeletedV1)
def handle_tournament_deleted(event: TournamentDeletedV1):
    """
    Handle the TournamentDeletedV1 event by performing necessary cleanup or updates.
    """
    logger.info(
        f"Received TournamentDeletedV1 event for tournament_id: {event.data.tournament_id}"
    )

    with get_db() as db:
        matches = (
            db.query(Match)
            .filter(Match.tournament_id == event.data.tournament_id)
            .all()
        )

        logger.info(
            f"Found {len(matches)} matches associated with tournament_id: {event.data.tournament_id}. Deleting them."
        )
        for match in matches:
            db.delete(match)
        db.commit()
