"""
Event handling for Ranking Service.
"""

from taca_messaging import RabbitMQService

from .logger import logger

rabbitmq_service = RabbitMQService(service_name="ranking-service")


# Event Publishers
async def publish_rankings_updated(season_id, scope, entity_id=None):
    """Publish RankingsUpdated event."""
    if not rabbitmq_service:
        return

    event_data = {}

    await rabbitmq_service.publish_event("rankings.updated", event_data)
    logger.info(f"Published rankings.updated event for scope {scope}")


@rabbitmq_service.event_handler("match.finished")
async def handle_match_finished(data: dict):
    """
    Consumes: match.finished

    Update rankings incrementally when a match finishes.
    Recalculate affected rankings (modality, course, general).
    """
    match_id = data.get("match_id")
    # tournament_id = data.get("tournament_id")
    logger.info(f"Handling match.finished event for match {match_id}")

    # Implementation to be added when database operations are needed
    # - Get tournament and modality info
    # - Apply scoring schema
    # - Update modality rankings
    # - Recalculate course rankings
    # - Recalculate general rankings
    # - Publish rankings.updated event
    logger.warning("MatchFinished handler not fully implemented yet")


@rabbitmq_service.event_handler("tournament.finished")
async def handle_tournament_finished(data: dict):
    """
    Consumes: tournament.finished

    Force complete recalculation of modality rankings when tournament finishes.
    Consolidate final points.
    """
    tournament_id = data.get("tournament_id")
    # modality_id = data.get("modality_id")
    logger.info(f"Handling tournament.finished event for tournament {tournament_id}")

    # Implementation to be added when database operations are needed
    # - Recalculate all rankings for this modality
    # - Ensure all matches are counted
    # - Update course rankings
    # - Update general rankings
    # - Publish rankings.updated event
    logger.warning("TournamentFinished handler not fully implemented yet")


@rabbitmq_service.event_handler("season.finished")
async def handle_season_finished(data: dict):
    """
    Consumes: season.finished

    Archive final rankings for the season.
    Create historical snapshot.
    """
    season_id = data.get("season_id")
    logger.info(f"Handling season.finished event for season {season_id}")

    # Implementation to be added when database operations are needed
    # - Archive all rankings for this season
    # - Create snapshot for historical queries
    # - Mark season as closed
    logger.warning("SeasonFinished handler not fully implemented yet")
