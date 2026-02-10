"""
Event handling for read-model-updater.
Publishes and consumes events via RabbitMQ.
"""

from typing import Any, Dict

from taca_events import RoutingKeys
from taca_messaging.rabbitmq_service import RabbitMQService

from .database import get_db
from .logger import logger

# Initialize RabbitMQ service for read-model-updater
rabbitmq_service = RabbitMQService(service_name="read-model-updater", logger=logger)


# ==================== Tournament Events ====================


@rabbitmq_service.event_handler(RoutingKeys.TOURNAMENT_CREATED)
def handle_tournament_created(event_data: Dict[str, Any]):
    """
    Handle tournament created event.

    Updates TournamentView with new tournament data.
    """
    tournament_id = event_data.get("tournament_id")
    logger.info(
        "event_received", event_type="tournament.created", tournament_id=tournament_id
    )

    with get_db() as db:
        # Placeholder for actual DB operations to create TournamentView entry
        print(db)  # To avoid "unused variable" warning
        pass


@rabbitmq_service.event_handler(RoutingKeys.TOURNAMENT_UPDATED)
def handle_tournament_updated(event_data: Dict[str, Any]):
    """
    Handle tournament updated event.

    Updates TournamentView with changed tournament data.
    """
    tournament_id = event_data.get("tournament_id")
    logger.info(
        "event_received", event_type="tournament.updated", tournament_id=tournament_id
    )


@rabbitmq_service.event_handler(RoutingKeys.TOURNAMENT_DELETED)
def handle_tournament_deleted(event_data: Dict[str, Any]):
    """
    Handle tournament deleted event.

    Removes tournament from TournamentView and cascades to related views.
    """
    tournament_id = event_data.get("tournament_id")
    logger.info(
        "event_received", event_type="tournament.deleted", tournament_id=tournament_id
    )


@rabbitmq_service.event_handler(RoutingKeys.TOURNAMENT_COMPETITOR_ADDED)
def handle_tournament_competitor_added(event_data: Dict[str, Any]):
    """
    Handle tournament competitor added event.

    Increments team_count in TournamentView.
    """
    tournament_id = event_data.get("tournament_id")
    logger.info(
        "event_received",
        event_type="tournament.competitor.added",
        tournament_id=tournament_id,
    )


@rabbitmq_service.event_handler(RoutingKeys.TOURNAMENT_COMPETITOR_DELETED)
def handle_tournament_competitor_deleted(event_data: Dict[str, Any]):
    """
    Handle tournament competitor deleted event.

    Decrements team_count in TournamentView.
    """
    tournament_id = event_data.get("tournament_id")
    logger.info(
        "event_received",
        event_type="tournament.competitor.deleted",
        tournament_id=tournament_id,
    )


# ==================== Match Events ====================


@rabbitmq_service.event_handler(RoutingKeys.MATCH_CREATED)
def handle_match_created(event_data: Dict[str, Any]):
    """
    Handle match created event.

    Creates GamesView entry and GameParticipantView entries for all participants.
    """
    match_id = event_data.get("match_id")
    logger.info("event_received", event_type="match.created", match_id=match_id)


@rabbitmq_service.event_handler(RoutingKeys.MATCH_UPDATED)
def handle_match_updated(event_data: Dict[str, Any]):
    """
    Handle match updated event.

    Updates GamesView with changed match data.
    """
    match_id = event_data.get("match_id")
    logger.info("event_received", event_type="match.updated", match_id=match_id)


@rabbitmq_service.event_handler(RoutingKeys.MATCH_DELETED)
def handle_match_deleted(event_data: Dict[str, Any]):
    """
    Handle match deleted event.

    Removes match and its participants from views.
    """
    match_id = event_data.get("match_id")
    logger.info("event_received", event_type="match.deleted", match_id=match_id)


@rabbitmq_service.event_handler(RoutingKeys.MATCH_RESULT_UPDATED)
def handle_match_result_updated(event_data: Dict[str, Any]):
    """
    Handle match result updated event.

    Updates GameParticipantView with scores/positions for all participants.
    """
    match_id = event_data.get("match_id")
    results = event_data.get("results", [])
    logger.info(
        "event_received",
        event_type="match.result.updated",
        match_id=match_id,
        results_count=len(results),
    )


# ==================== Modality Events ====================


@rabbitmq_service.event_handler(RoutingKeys.MODALITY_UPDATED)
def handle_modality_updated(event_data: Dict[str, Any]):
    """
    Handle modality updated event.

    Updates modality name in all related views.
    """
    modality_id = event_data.get("modality_id")
    logger.info(
        "event_received", event_type="modality.updated", modality_id=modality_id
    )


@rabbitmq_service.event_handler(RoutingKeys.TEAM_UPDATED)
def handle_team_updated(event_data: Dict[str, Any]):
    """
    Handle team updated event.

    Updates team name in all related views.
    """
    team_id = event_data.get("team_id")
    logger.info("event_received", event_type="team.updated", team_id=team_id)


@rabbitmq_service.event_handler(RoutingKeys.COURSE_UPDATED)
def handle_course_updated(event_data: Dict[str, Any]):
    """
    Handle course updated event.

    Updates course name in all related views.
    """
    course_id = event_data.get("course_id")
    logger.info("event_received", event_type="course.updated", course_id=course_id)


# ==================== Nucleo Events ====================


@rabbitmq_service.event_handler(RoutingKeys.NUCLEO_CREATED)
def handle_nucleo_created(event_data: Dict[str, Any]):
    """
    Handle nucleo created event.
    """
    logger.info(
        "event_received",
        event_type="nucleo.created",
        nucleo_id=event_data.get("nucleo_id"),
    )


@rabbitmq_service.event_handler(RoutingKeys.NUCLEO_UPDATED)
def handle_nucleo_updated(event_data: Dict[str, Any]):
    """
    Handle nucleo updated event.
    """
    nucleo_id = event_data.get("nucleo_id") or event_data.get("id")
    logger.info("event_received", event_type="nucleo.updated", nucleo_id=nucleo_id)


@rabbitmq_service.event_handler(RoutingKeys.NUCLEO_DELETED)
def handle_nucleo_deleted(event_data: Dict[str, Any]):
    """
    Handle nucleo deleted event.
    """
    logger.info(
        "event_received",
        event_type="nucleo.deleted",
        nucleo_id=event_data.get("nucleo_id"),
    )
