"""
Event handling for Ranking Service.
"""

from taca_events import modalities, tournaments
from taca_messaging import RabbitMQService

from .database import get_db
from .logger import logger
from .models import (
    Course,
    Modality,
    ModalityType,
    ModalityTypeEscalao,
    Tournament,
    TournamentCompetitor,
    TournamentResult,
)

rabbitmq_service = RabbitMQService(service_name="ranking-service")


# ==================== Modality Type Events ====================


@rabbitmq_service.event_handler(modalities.ModalityTypeCreatedV1)
def handle_modality_type_created(event: modalities.ModalityTypeCreatedV1):
    """Handle modality type created event."""
    modality_type_id = event.data.modality_type_id
    escaloes_data = event.data.escaloes
    logger.info(
        "event_received",
        event_type="modality_type.created",
        modality_type_id=str(modality_type_id),
    )

    with get_db() as db:
        modality_type = ModalityType(
            modality_type_id=modality_type_id,
        )
        db.add(modality_type)

        for escalao_data in escaloes_data:
            escalao = ModalityTypeEscalao(
                modality_type_id=modality_type_id,
                min_participants=escalao_data.min_participants,
                max_participants=escalao_data.max_participants,
                points=escalao_data.points,
            )
            db.add(escalao)
        db.flush()


@rabbitmq_service.event_handler(modalities.ModalityTypeUpdatedV1)
def handle_modality_type_updated(event: modalities.ModalityTypeUpdatedV1):
    """Handle modality type updated event."""
    modality_type_id = event.data.modality_type_id
    escaloes_data = event.data.escaloes

    logger.info(
        "event_received",
        event_type="modality_type.updated",
        modality_type_id=str(modality_type_id),
    )

    with get_db() as db:
        modality_type = (
            db.query(ModalityType)
            .filter(ModalityType.modality_type_id == modality_type_id)
            .first()
        )
        if not modality_type:
            logger.warning(
                "modality_type_not_found", modality_type_id=str(modality_type_id)
            )
            return

        # Update modality type id if provided
        if event.data.modality_type_id is not None:
            modality_type.modality_type_id = event.data.modality_type_id
            db.flush()

        # Update escaloes if provided
        if escaloes_data is not None:
            # Delete existing escaloes
            db.query(ModalityTypeEscalao).filter(
                ModalityTypeEscalao.modality_type_id
                == modality_type.modality_type_id  # Use the updated or not modality_type_id for filtering
            ).delete()

            # Add new escaloes
            for escalao_data in escaloes_data:
                escalao = ModalityTypeEscalao(
                    modality_type_id=modality_type.modality_type_id,
                    min_participants=escalao_data.min_participants,
                    max_participants=escalao_data.max_participants,
                    points=escalao_data.points,
                )
                db.add(escalao)
        db.flush()


@rabbitmq_service.event_handler(modalities.ModalityTypeDeletedV1)
def handle_modality_type_deleted(event: modalities.ModalityTypeDeletedV1):
    """Handle modality type deleted event."""
    modality_type_id = event.data.modality_type_id
    logger.info(
        "event_received",
        event_type="modality_type.deleted",
        modality_type_id=str(modality_type_id),
    )

    with get_db() as db:
        modality_type = (
            db.query(ModalityType)
            .filter(ModalityType.modality_type_id == modality_type_id)
            .first()
        )
        if not modality_type:
            logger.warning(
                "modality_type_not_found", modality_type_id=str(modality_type_id)
            )
            return
        db.delete(modality_type)
        db.flush()


# ==================== Modality Events ====================


@rabbitmq_service.event_handler(modalities.ModalityCreatedV1)
def handle_modality_created(event: modalities.ModalityCreatedV1):
    """Handle modality created event."""
    modality_id = event.data.modality_id
    logger.info(
        "event_received", event_type="modality.created", modality_id=str(modality_id)
    )

    with get_db() as db:
        modality = Modality(
            modality_id=modality_id,
            modality_type_id=event.data.modality_type_id,
        )
        db.add(modality)


@rabbitmq_service.event_handler(modalities.ModalityUpdatedV1)
def handle_modality_updated(event: modalities.ModalityUpdatedV1):
    """Handle modality updated event."""
    modality_id = event.data.modality_id
    logger.info(
        "event_received", event_type="modality.updated", modality_id=str(modality_id)
    )

    with get_db() as db:
        modality = (
            db.query(Modality).filter(Modality.modality_id == modality_id).first()
        )
        if not modality:
            logger.warning("modality_not_found", modality_id=str(modality_id))
            return

        # Update id
        if event.data.modality_type_id is not None:
            modality.modality_type_id = event.data.modality_type_id
        db.flush()

        # Update escaloes if provided


@rabbitmq_service.event_handler(modalities.ModalityDeletedV1)
def handle_modality_deleted(event: modalities.ModalityDeletedV1):
    """Handle modality deleted event."""
    modality_id = event.data.modality_id
    logger.info(
        "event_received", event_type="modality.deleted", modality_id=str(modality_id)
    )

    with get_db() as db:
        modality = (
            db.query(Modality).filter(Modality.modality_id == modality_id).first()
        )
        if not modality:
            logger.warning("modality_not_found", modality_id=str(modality_id))
            return
        db.delete(modality)


# ==================== Tournament Events ====================


@rabbitmq_service.event_handler(tournaments.TournamentCreatedV1)
def handle_tournament_created(event: tournaments.TournamentCreatedV1):
    """Handle tournament created event."""
    tournament_id = event.data.tournament_id
    logger.info(
        "event_received",
        event_type="tournament.created",
        tournament_id=str(tournament_id),
    )

    with get_db() as db:
        tournament = Tournament(
            tournament_id=tournament_id,
            modality_id=event.data.modality_id,
        )
        db.add(tournament)
        db.flush()


@rabbitmq_service.event_handler(tournaments.TournamentDeletedV1)
def handle_tournament_deleted(event: tournaments.TournamentDeletedV1):
    """Handle tournament deleted event.

    Soft-deletes the tournament and cascades to competitors and matches.
    """
    tournament_id = event.data.tournament_id
    logger.info(
        "event_received",
        event_type="tournament.deleted",
        tournament_id=str(tournament_id),
    )

    with get_db() as db:
        tournament = (
            db.query(Tournament)
            .filter(Tournament.tournament_id == tournament_id)
            .first()
        )
        if not tournament:
            logger.warning("tournament_not_found", tournament_id=str(tournament_id))
            return
        tournament.delete()
        db.flush()


@rabbitmq_service.event_handler(tournaments.TournamentFinishedV1)
def handle_tournament_finished(event: tournaments.TournamentFinishedV1):
    """Handle tournament finished event."""
    tournament_id = event.data.tournament_id
    ranking_entries = event.data.ranking_entries

    logger.info(
        "event_received",
        event_type="tournament.finished",
        tournament_id=str(tournament_id),
        ranking_entries_count=len(ranking_entries),
    )

    with get_db() as db:
        tournament = (
            db.query(Tournament)
            .filter(Tournament.tournament_id == tournament_id)
            .first()
        )
        if not tournament:
            logger.warning("tournament_not_found", tournament_id=str(tournament_id))
            return

        # Create new ranking entries
        for entry in ranking_entries:
            ranking = TournamentResult(
                tournament_id=tournament_id,
                competitor_id=entry.competitor_id,
                position=entry.position,
            )
            db.add(ranking)

        db.flush()

        logger.info(
            "tournament_rankings_stored",
            tournament_id=str(tournament_id),
            ranking_entries_count=len(ranking_entries),
        )


@rabbitmq_service.event_handler(tournaments.TournamentCompetitorAddedV1)
def handle_tournament_competitor_added(event: tournaments.TournamentCompetitorAddedV1):
    """Handle tournament competitor added event."""
    tournament_id = event.data.tournament_id
    competitor_id = event.data.competitor_id
    logger.info(
        "event_received",
        event_type="tournament.competitor.added",
        tournament_id=str(tournament_id),
    )

    with get_db() as db:
        competitor = TournamentCompetitor(
            competitor_id=competitor_id,
            tournament_id=tournament_id,
        )
        db.add(competitor)
        db.flush()


@rabbitmq_service.event_handler(tournaments.TournamentCompetitorDeletedV1)
def handle_tournament_competitor_deleted(
    event: tournaments.TournamentCompetitorDeletedV1,
):
    """Handle tournament competitor deleted event."""
    tournament_id = event.data.tournament_id
    competitor_id = event.data.competitor_id
    logger.info(
        "event_received",
        event_type="tournament.competitor.deleted",
        tournament_id=str(tournament_id),
    )

    with get_db() as db:
        competitor = (
            db.query(TournamentCompetitor)
            .filter(
                TournamentCompetitor.competitor_id == competitor_id,
                TournamentCompetitor.tournament_id == tournament_id,
            )
            .first()
        )

        if not competitor:
            logger.warning(
                "tournament_competitor_not_found", tournament_id=str(tournament_id)
            )
            return
        db.flush()


# ==================== Course Events ====================
@rabbitmq_service.event_handler(modalities.CourseCreatedV1)
def handle_course_created(event: modalities.CourseCreatedV1):
    """Handle course created event."""
    course_id = event.data.course_id
    logger.info("event_received", event_type="course.created", course_id=str(course_id))

    with get_db() as db:
        course = Course(course_id=course_id)
        db.add(course)
        db.flush()


@rabbitmq_service.event_handler(modalities.CourseDeletedV1)
def handle_course_deleted(event: modalities.CourseDeletedV1):
    """Handle course deleted event."""
    course_id = event.data.course_id
    logger.info("event_received", event_type="course.deleted", course_id=str(course_id))

    with get_db() as db:
        course = db.query(Course).filter(Course.course_id == course_id).first()
        if not course:
            logger.warning("course_not_found", course_id=str(course_id))
            return
