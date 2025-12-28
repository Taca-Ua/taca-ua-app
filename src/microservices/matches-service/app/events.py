"""
Event handling for Matches Service.
"""

from datetime import datetime, timezone

from taca_messaging.rabbitmq_service import RabbitMQService

from .logger import logger
from .models import Match

rabbitmq_service = RabbitMQService(service_name="matches-service")


# Event Publishers
async def publish_match_created(match: Match):
    """Publish MatchCreated event."""
    if not rabbitmq_service:
        return

    event_data = {
        "match_id": str(match.id),
        "tournament_id": str(match.tournament_id),
        "team_home_id": str(match.team_home_id),
        "team_away_id": str(match.team_away_id),
        "start_time": match.start_time.isoformat(),
        "created_at": match.created_at.isoformat(),
    }

    await rabbitmq_service.publish_event("match.created", event_data)
    logger.info(f"Published match.created event for match {match.id}")


async def publish_match_updated(match: Match, changes):
    """Publish MatchUpdated event."""
    if not rabbitmq_service:
        return

    event_data = {
        "match_id": str(match.id),
        "changes": changes,
        "updated_at": match.updated_at.isoformat() if match.updated_at else None,
    }

    await rabbitmq_service.publish_event("match.updated", event_data)
    logger.info(f"Published match.updated event for match {match.id}")


async def publish_match_finished(match: Match):
    """Publish MatchFinished event."""
    if not rabbitmq_service:
        return

    event_data = {
        "match_id": str(match.id),
        "tournament_id": str(match.tournament_id),
        "team_home_id": str(match.team_home_id),
        "team_away_id": str(match.team_away_id),
        "home_score": match.home_score,
        "away_score": match.away_score,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }

    await rabbitmq_service.publish_event("match.finished", event_data)
    logger.info(f"Published match.finished event for match {match.id}")


async def publish_match_cancelled(match_id, reason):
    """Publish MatchCancelled event."""
    if not rabbitmq_service:
        return

    event_data = {
        "match_id": str(match_id),
        "reason": reason,
        "cancelled_at": datetime.now(timezone.utc).isoformat(),
    }

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
