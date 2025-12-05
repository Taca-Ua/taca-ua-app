"""
Event handling for Matches Service.
"""

from taca_messaging.rabbitmq_service import RabbitMQService

from .logger import logger

rabbitmq_service = RabbitMQService(service_name="matches-service")


class FakeMatch:
    """Temporary placeholder for Match object when None is provided."""

    def __init__(self, _id):
        self.id = _id


# Event Publishers
async def publish_match_created(match):
    """Publish MatchCreated event."""
    if not rabbitmq_service:
        return

    if match is None:
        match = FakeMatch(_id="unknown")

    event_data = {}

    await rabbitmq_service.publish_event("match.created", event_data)
    logger.info(f"Published match.created event for match {match.id}")


async def publish_match_updated(match, changes):
    """Publish MatchUpdated event."""
    if not rabbitmq_service:
        return

    if match is None:
        match = FakeMatch(_id="unknown")

    event_data = {}

    await rabbitmq_service.publish_event("match.updated", event_data)
    logger.info(f"Published match.updated event for match {match.id}")


async def publish_match_finished(match):
    """Publish MatchFinished event."""
    if not rabbitmq_service:
        return

    if match is None:
        match = FakeMatch(_id="unknown")

    event_data = {}

    await rabbitmq_service.publish_event("match.finished", event_data)
    logger.info(f"Published match.finished event for match {match.id}")


async def publish_match_cancelled(match_id, reason):
    """Publish MatchCancelled event."""
    if not rabbitmq_service:
        return

    event_data = {}

    await rabbitmq_service.publish_event("match.cancelled", event_data)
    logger.info(f"Published match.cancelled event for match {match_id}")


# Event Handlers
@rabbitmq_service.event_handler("tournament.finished")
async def handle_tournament_finished(data: dict):
    """
    Consumes: tournament.finished

    Finalize all pending matches of the tournament.
    """
    tournament_id = data.get("tournament_id")
    logger.info(f"Handling tournament.finished event for tournament {tournament_id}")

    # Implementation to be added when database operations are needed
    # - Find all matches with this tournament_id that are not finished
    # - Mark them as cancelled
    # - Publish match.cancelled events
    logger.warning("TournamentFinished handler not fully implemented yet")


@rabbitmq_service.event_handler("team.deleted")
async def handle_team_deleted(data: dict):
    """
    Consumes: team.deleted

    Cancel all future matches of this team.
    """
    team_id = data.get("team_id")
    logger.info(f"Handling team.deleted event for team {team_id}")

    # Implementation to be added when database operations are needed
    # - Find all future matches with this team_id
    # - Mark them as cancelled
    # - Publish match.cancelled events
    logger.warning("TeamDeleted handler not fully implemented yet")
