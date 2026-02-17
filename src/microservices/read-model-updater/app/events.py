"""
Event handling for read-model-updater.
Publishes and consumes events via RabbitMQ.

Supports pause/resume for rebuild operations.
"""

from typing import Any, Dict

from taca_events import RoutingKeys
from taca_messaging.rabbitmq_service import RabbitMQService

from .database import get_db
from .logger import logger


class PausableRabbitMQService(RabbitMQService):
    """
    Extended RabbitMQ service with pause/resume capabilities.

    This is needed for the rebuild process to temporarily stop
    event consumption while projections are being rebuilt.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._paused = False
        self._original_on_message = None

    def is_paused(self) -> bool:
        """Check if event consumption is currently paused."""
        return self._paused

    async def pause_consumption(self) -> None:
        """
        Pause event consumption.

        Events will be buffered in RabbitMQ queue but not processed
        until consumption is resumed.
        """
        if self._paused:
            self.logger.warning("event_consumption_already_paused")
            return

        self._paused = True

        # Cancel the consumer to stop receiving messages
        # Messages will remain in the queue
        if self.channel and hasattr(self.channel, "_consumers"):
            # Store consumer tags to cancel them
            consumer_tags = (
                list(self.channel._consumers.keys())
                if hasattr(self.channel, "_consumers")
                else []
            )
            for tag in consumer_tags:
                try:
                    await self.channel.cancel(tag)
                    self.logger.info("consumer_cancelled", consumer_tag=tag)
                except Exception as e:
                    self.logger.error(
                        "consumer_cancel_failed", consumer_tag=tag, error=str(e)
                    )

        self.logger.info(
            "event_consumption_paused",
            message="Events will queue but not be processed",
        )

    async def resume_consumption(self) -> None:
        """
        Resume event consumption.

        Starts processing events from the queue again.
        """
        if not self._paused:
            self.logger.warning("event_consumption_not_paused")
            return

        self._paused = False

        # Restart consuming by calling start_consuming again
        # This will re-bind to the queue and start processing
        try:
            await self.start_consuming()
            self.logger.info("event_consumption_resumed")
        except Exception as e:
            self.logger.error("event_consumption_resume_failed", error=str(e))
            raise


# Initialize RabbitMQ service with pause/resume capabilities
rabbitmq_service = PausableRabbitMQService(
    service_name="read-model-updater", logger=logger
)


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
