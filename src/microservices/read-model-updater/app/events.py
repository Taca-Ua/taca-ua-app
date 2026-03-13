"""
Event handling for read-model-updater.
Publishes and consumes events via RabbitMQ.

Supports pause/resume for rebuild operations.
"""

import uuid
from datetime import date, datetime, timezone
from typing import Any

from taca_events.pydantic_schemas import (  # Nucleo; Course; Modality Type; Modality; Student; Staff; Team; Tournament; Match; Ranking
    CourseCreatedV1,
    CourseDeletedV1,
    CourseUpdatedV1,
    MatchCommentAddedV1,
    MatchCommentDeletedV1,
    MatchCreatedV1,
    MatchDeletedV1,
    MatchLineupAssignedV1,
    MatchParticipantAddedV1,
    MatchParticipantRemovedV1,
    MatchResultUpdatedV1,
    MatchUpdatedV1,
    ModalityCreatedV1,
    ModalityDeletedV1,
    ModalityTypeCreatedV1,
    ModalityTypeDeletedV1,
    ModalityTypeUpdatedV1,
    ModalityUpdatedV1,
    NucleoCreatedV1,
    NucleoDeletedV1,
    NucleoUpdatedV1,
    RankingComputedV1,
    StaffCreatedV1,
    StaffDeletedV1,
    StaffUpdatedV1,
    StudentCreatedV1,
    StudentDeletedV1,
    StudentUpdatedV1,
    TeamCreatedV1,
    TeamDeletedV1,
    TeamPlayerAddedV1,
    TeamPlayerRemovedV1,
    TeamUpdatedV1,
    TournamentCompetitorAddedV1,
    TournamentCompetitorDeletedV1,
    TournamentCreatedV1,
    TournamentDeletedV1,
    TournamentFinishedV1,
    TournamentUpdatedV1,
)
from taca_messaging.rabbitmq_service import RabbitMQService

from .database import get_db
from .logger import logger
from .models import (
    Course,
    GeneralRankingView,
    Match,
    MatchComment,
    MatchLineup,
    MatchParticipant,
    MatchResult,
    MatchStatus,
    Modality,
    ModalityType,
    Nucleo,
    ParticipantType,
    Staff,
    Student,
    Team,
    TeamPlayer,
    Tournament,
    TournamentCompetitor,
    TournamentRanking,
)
from .utils import (
    rebuild_all_students_for_course,
    rebuild_all_teams_for_course,
    rebuild_all_teams_for_modality,
    rebuild_all_tournaments_for_modality,
    rebuild_match_projection,
    rebuild_student_projection,
    rebuild_team_projection,
    rebuild_tournament_projection,
    rebuild_tournament_standings,
)


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


# ==================== Helpers ====================


def _parse_dt(value: Any) -> datetime:
    """Parse an ISO 8601 datetime string to a naive UTC datetime."""
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _parse_date(value: Any) -> date:
    """Parse an ISO 8601 date string to a date object."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value)[:10])


# ==================== Nucleo Events ====================


@rabbitmq_service.event_handler(NucleoCreatedV1)
def handle_nucleo_created(event: NucleoCreatedV1):
    """Handle nucleo created event."""
    nucleo_id = event.data.nucleo_id
    logger.info("event_received", event_type="nucleo.created", nucleo_id=str(nucleo_id))

    with get_db() as db:
        nucleo = Nucleo(
            nucleo_id=nucleo_id,
            name=event.data.name,
            abbreviation=event.data.abbreviation,
        )
        db.add(nucleo)


@rabbitmq_service.event_handler(NucleoUpdatedV1)
def handle_nucleo_updated(event: NucleoUpdatedV1):
    """Handle nucleo updated event."""
    nucleo_id = event.data.nucleo_id
    logger.info("event_received", event_type="nucleo.updated", nucleo_id=str(nucleo_id))

    with get_db() as db:
        nucleo = db.query(Nucleo).filter(Nucleo.nucleo_id == nucleo_id).first()
        if not nucleo:
            logger.warning("nucleo_not_found", nucleo_id=str(nucleo_id))
            return
        if event.data.name is not None:
            nucleo.name = event.data.name
        if event.data.abbreviation is not None:
            nucleo.abbreviation = event.data.abbreviation
        nucleo.updated_at = datetime.utcnow()

        # Rebuild affected projections
        db.flush()
        courses = db.query(Course.course_id).filter(Course.nucleo_id == nucleo_id).all()
        for (course_id,) in courses:
            rebuild_all_teams_for_course(db, course_id)
            rebuild_all_students_for_course(db, course_id)


@rabbitmq_service.event_handler(NucleoDeletedV1)
def handle_nucleo_deleted(event: NucleoDeletedV1):
    """Handle nucleo deleted event."""
    nucleo_id = event.data.nucleo_id
    logger.info("event_received", event_type="nucleo.deleted", nucleo_id=str(nucleo_id))

    with get_db() as db:
        nucleo = db.query(Nucleo).filter(Nucleo.nucleo_id == nucleo_id).first()
        if not nucleo:
            logger.warning("nucleo_not_found", nucleo_id=str(nucleo_id))
            return
        nucleo.deleted_at = datetime.utcnow()


# ==================== Course Events ====================


@rabbitmq_service.event_handler(CourseCreatedV1)
def handle_course_created(event: CourseCreatedV1):
    """Handle course created event."""
    course_id = event.data.course_id
    logger.info("event_received", event_type="course.created", course_id=str(course_id))

    with get_db() as db:
        course = Course(
            course_id=course_id,
            nucleo_id=event.data.nucleo_id,
            name=event.data.name,
            abbreviation=event.data.abbreviation,
        )
        db.add(course)


@rabbitmq_service.event_handler(CourseUpdatedV1)
def handle_course_updated(event: CourseUpdatedV1):
    """Handle course updated event."""
    course_id = event.data.course_id
    logger.info("event_received", event_type="course.updated", course_id=str(course_id))

    with get_db() as db:
        course = db.query(Course).filter(Course.course_id == course_id).first()
        if not course:
            logger.warning("course_not_found", course_id=str(course_id))
            return
        if event.data.name is not None:
            course.name = event.data.name
        if event.data.abbreviation is not None:
            course.abbreviation = event.data.abbreviation
        if event.data.nucleo_id is not None:
            course.nucleo_id = event.data.nucleo_id
        course.updated_at = datetime.utcnow()

        # Rebuild affected projections
        db.flush()
        rebuild_all_teams_for_course(db, course_id)
        rebuild_all_students_for_course(db, course_id)


@rabbitmq_service.event_handler(CourseDeletedV1)
def handle_course_deleted(event: CourseDeletedV1):
    """Handle course deleted event."""
    course_id = event.data.course_id
    logger.info("event_received", event_type="course.deleted", course_id=str(course_id))

    with get_db() as db:
        course = db.query(Course).filter(Course.course_id == course_id).first()
        if not course:
            logger.warning("course_not_found", course_id=str(course_id))
            return
        course.deleted_at = datetime.utcnow()


# ==================== Modality Type Events ====================


@rabbitmq_service.event_handler(ModalityTypeCreatedV1)
def handle_modality_type_created(event: ModalityTypeCreatedV1):
    """Handle modality type created event."""
    modality_type_id = event.data.modality_type_id
    logger.info(
        "event_received",
        event_type="modality_type.created",
        modality_type_id=str(modality_type_id),
    )

    with get_db() as db:
        modality_type = ModalityType(
            modality_type_id=modality_type_id,
            name=event.data.name,
            description=event.data.description,
            escaloes=event.data.escaloes,
        )
        db.add(modality_type)


@rabbitmq_service.event_handler(ModalityTypeUpdatedV1)
def handle_modality_type_updated(event: ModalityTypeUpdatedV1):
    """Handle modality type updated event."""
    modality_type_id = event.data.modality_type_id
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
        if event.data.name is not None:
            modality_type.name = event.data.name
        if event.data.description is not None:
            modality_type.description = event.data.description
        if event.data.escaloes is not None:
            modality_type.escaloes = event.data.escaloes

        modality_type.updated_at = datetime.utcnow()


@rabbitmq_service.event_handler(ModalityTypeDeletedV1)
def handle_modality_type_deleted(event: ModalityTypeDeletedV1):
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
        modality_type.deleted_at = datetime.utcnow()


# ==================== Modality Events ====================


@rabbitmq_service.event_handler(ModalityCreatedV1)
def handle_modality_created(event: ModalityCreatedV1):
    """Handle modality created event."""
    modality_id = event.data.modality_id
    logger.info(
        "event_received", event_type="modality.created", modality_id=str(modality_id)
    )

    with get_db() as db:
        modality = Modality(
            modality_id=modality_id,
            modality_type_id=event.data.modality_type_id,
            name=event.data.name,
        )
        db.add(modality)


@rabbitmq_service.event_handler(ModalityUpdatedV1)
def handle_modality_updated(event: ModalityUpdatedV1):
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
        if event.data.name is not None:
            modality.name = event.data.name
        if event.data.modality_type_id is not None:
            modality.modality_type_id = event.data.modality_type_id
        modality.updated_at = datetime.utcnow()
        db.flush()
        # Rebuild affected projections
        rebuild_all_teams_for_modality(db, modality_id)
        rebuild_all_tournaments_for_modality(db, modality_id)


@rabbitmq_service.event_handler(ModalityDeletedV1)
def handle_modality_deleted(event: ModalityDeletedV1):
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
        modality.deleted_at = datetime.utcnow()


# ==================== Student Events ====================


@rabbitmq_service.event_handler(StudentCreatedV1)
def handle_student_created(event: StudentCreatedV1):
    """Handle student created event."""
    student_id = event.data.student_id
    logger.info(
        "event_received", event_type="student.created", student_id=str(student_id)
    )

    with get_db() as db:
        student = Student(
            student_id=student_id,
            course_id=event.data.course_id,
            student_number=event.data.student_number,
            full_name=event.data.full_name,
            is_member=event.data.is_member,
        )
        db.add(student)
        db.flush()
        rebuild_student_projection(db, student_id)


@rabbitmq_service.event_handler(StudentUpdatedV1)
def handle_student_updated(event: StudentUpdatedV1):
    """Handle student updated event."""
    student_id = event.data.student_id
    logger.info(
        "event_received", event_type="student.updated", student_id=str(student_id)
    )

    with get_db() as db:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            logger.warning("student_not_found", student_id=str(student_id))
            return
        if event.data.full_name is not None:
            student.full_name = event.data.full_name
        if event.data.course_id is not None:
            student.course_id = event.data.course_id
        if event.data.student_number is not None:
            student.student_number = event.data.student_number
        if event.data.is_member is not None:
            student.is_member = event.data.is_member
        student.updated_at = datetime.utcnow()
        db.flush()
        rebuild_student_projection(db, student_id)


@rabbitmq_service.event_handler(StudentDeletedV1)
def handle_student_deleted(event: StudentDeletedV1):
    """Handle student deleted event."""
    student_id = event.data.student_id
    logger.info(
        "event_received", event_type="student.deleted", student_id=str(student_id)
    )

    with get_db() as db:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            logger.warning("student_not_found", student_id=str(student_id))
            return
        student.deleted_at = datetime.utcnow()
        db.flush()
        rebuild_student_projection(db, student_id)


# ==================== Staff Events ====================


@rabbitmq_service.event_handler(StaffCreatedV1)
def handle_staff_created(event: StaffCreatedV1):
    """Handle staff created event."""
    staff_id = event.data.staff_id
    logger.info("event_received", event_type="staff.created", staff_id=str(staff_id))

    with get_db() as db:
        staff = Staff(
            staff_id=staff_id,
            full_name=event.data.full_name,
            staff_number=event.data.staff_number,
            contact=event.data.contact,
        )
        db.add(staff)


@rabbitmq_service.event_handler(StaffUpdatedV1)
def handle_staff_updated(event: StaffUpdatedV1):
    """Handle staff updated event."""
    staff_id = event.data.staff_id
    logger.info("event_received", event_type="staff.updated", staff_id=str(staff_id))

    with get_db() as db:
        staff = db.query(Staff).filter(Staff.staff_id == staff_id).first()
        if not staff:
            logger.warning("staff_not_found", staff_id=str(staff_id))
            return
        if event.data.full_name is not None:
            staff.full_name = event.data.full_name
        if event.data.staff_number is not None:
            staff.staff_number = event.data.staff_number
        if event.data.contact is not None:
            staff.contact = event.data.contact
        staff.updated_at = datetime.utcnow()


@rabbitmq_service.event_handler(StaffDeletedV1)
def handle_staff_deleted(event: StaffDeletedV1):
    """Handle staff deleted event."""
    staff_id = event.data.staff_id
    logger.info("event_received", event_type="staff.deleted", staff_id=str(staff_id))

    with get_db() as db:
        staff = db.query(Staff).filter(Staff.staff_id == staff_id).first()
        if not staff:
            logger.warning("staff_not_found", staff_id=str(staff_id))
            return
        staff.deleted_at = datetime.utcnow()


# ==================== Team Events ====================


@rabbitmq_service.event_handler(TeamCreatedV1)
def handle_team_created(event: TeamCreatedV1):
    """Handle team created event."""
    team_id = event.data.team_id
    logger.info("event_received", event_type="team.created", team_id=str(team_id))

    with get_db() as db:
        team = Team(
            team_id=team_id,
            modality_id=event.data.modality_id,
            course_id=event.data.course_id,
            name=event.data.name,
        )
        db.add(team)
        db.flush()
        rebuild_team_projection(db, team_id)


@rabbitmq_service.event_handler(TeamUpdatedV1)
def handle_team_updated(event: TeamUpdatedV1):
    """Handle team updated event."""
    team_id = event.data.team_id
    logger.info("event_received", event_type="team.updated", team_id=str(team_id))

    with get_db() as db:
        team = db.query(Team).filter(Team.team_id == team_id).first()
        if not team:
            logger.warning("team_not_found", team_id=str(team_id))
            return
        if event.data.name is not None:
            team.name = event.data.name
        if event.data.modality_id is not None:
            team.modality_id = event.data.modality_id
        if event.data.course_id is not None:
            team.course_id = event.data.course_id
        team.updated_at = datetime.utcnow()
        db.flush()
        rebuild_team_projection(db, team_id)


@rabbitmq_service.event_handler(TeamDeletedV1)
def handle_team_deleted(event: TeamDeletedV1):
    """Handle team deleted event."""
    team_id = event.data.team_id
    logger.info("event_received", event_type="team.deleted", team_id=str(team_id))

    with get_db() as db:
        team = db.query(Team).filter(Team.team_id == team_id).first()
        if not team:
            logger.warning("team_not_found", team_id=str(team_id))
            return
        team.deleted_at = datetime.utcnow()
        db.flush()
        rebuild_team_projection(db, team_id)


@rabbitmq_service.event_handler(TeamPlayerAddedV1)
def handle_team_player_added(event: TeamPlayerAddedV1):
    """Handle team player added event."""
    team_id = event.data.team_id
    student_id = event.data.student_id
    logger.info(
        "event_received",
        event_type="team.player_added",
        team_id=str(team_id),
        student_id=str(student_id),
    )

    with get_db() as db:
        team_player = TeamPlayer(
            team_id=team_id,
            student_id=student_id,
        )
        db.add(team_player)
        db.flush()
        # Rebuild both team and student projections
        rebuild_team_projection(db, team_id)
        rebuild_student_projection(db, student_id)


@rabbitmq_service.event_handler(TeamPlayerRemovedV1)
def handle_team_player_removed(event: TeamPlayerRemovedV1):
    """Handle team player removed event."""
    team_id = event.data.team_id
    student_id = event.data.student_id
    logger.info(
        "event_received",
        event_type="team.player_removed",
        team_id=str(team_id),
        student_id=str(student_id),
    )

    with get_db() as db:
        team_player = (
            db.query(TeamPlayer)
            .filter(
                TeamPlayer.team_id == team_id,
                TeamPlayer.student_id == student_id,
                TeamPlayer.removed_at.is_(None),
            )
            .first()
        )
        if not team_player:
            logger.warning(
                "team_player_not_found",
                team_id=str(team_id),
                student_id=str(student_id),
            )
            return
        team_player.removed_at = datetime.utcnow()
        db.flush()
        # Rebuild both team and student projections
        rebuild_team_projection(db, team_id)
        rebuild_student_projection(db, student_id)


# ==================== Tournament Events ====================


@rabbitmq_service.event_handler(TournamentCreatedV1)
def handle_tournament_created(event: TournamentCreatedV1):
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
            name=event.data.name,
            start_date=_parse_date(event.data.start_date),
            status=event.data.status,
        )
        db.add(tournament)
        db.flush()
        rebuild_tournament_projection(db, tournament_id)


@rabbitmq_service.event_handler(TournamentUpdatedV1)
def handle_tournament_updated(event: TournamentUpdatedV1):
    """Handle tournament updated event."""
    tournament_id = event.data.tournament_id
    logger.info(
        "event_received",
        event_type="tournament.updated",
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
        if event.data.name is not None:
            tournament.name = event.data.name
        if event.data.start_date is not None:
            tournament.start_date = _parse_date(event.data.start_date)
        if event.data.status is not None:
            tournament.status = event.data.status
        tournament.updated_at = datetime.utcnow()
        db.flush()
        rebuild_tournament_projection(db, tournament_id)


@rabbitmq_service.event_handler(TournamentDeletedV1)
def handle_tournament_deleted(event: TournamentDeletedV1):
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
        now = datetime.utcnow()
        tournament.deleted_at = now
        db.query(TournamentCompetitor).filter(
            TournamentCompetitor.tournament_id == tournament_id,
            TournamentCompetitor.deleted_at.is_(None),
        ).update({"deleted_at": now})
        db.query(Match).filter(
            Match.tournament_id == tournament_id,
            Match.deleted_at.is_(None),
        ).update({"deleted_at": now})
        db.flush()
        rebuild_tournament_projection(db, tournament_id)


@rabbitmq_service.event_handler(TournamentFinishedV1)
def handle_tournament_finished(event: TournamentFinishedV1):
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

        now = datetime.utcnow()
        tournament.status = "finished"
        tournament.finished_at = now
        tournament.updated_at = now
        db.flush()

        # Delete existing ranking entries for this tournament (if any)
        db.query(TournamentRanking).filter(
            TournamentRanking.tournament_id == tournament_id
        ).delete()

        # Create new ranking entries
        for entry in ranking_entries:
            ranking = TournamentRanking(
                tournament_id=tournament_id,
                competitor_id=entry.competitor_id,
                position=entry.position,
                created_at=now,
            )
            db.add(ranking)

        db.flush()
        rebuild_tournament_projection(db, tournament_id)

        logger.info(
            "tournament_rankings_stored",
            tournament_id=str(tournament_id),
            ranking_entries_count=len(ranking_entries),
        )


@rabbitmq_service.event_handler(TournamentCompetitorAddedV1)
def handle_tournament_competitor_added(event: TournamentCompetitorAddedV1):
    """Handle tournament competitor added event."""
    tournament_id = event.data.tournament_id
    logger.info(
        "event_received",
        event_type="tournament.competitor.added",
        tournament_id=str(tournament_id),
    )

    with get_db() as db:
        competitor = TournamentCompetitor(
            competitor_id=uuid.uuid4(),
            tournament_id=tournament_id,
            competitor_type=ParticipantType(event.data.competitor_type),
            competitor_entity_id=event.data.competitor_entity_id,
        )
        db.add(competitor)
        db.flush()
        # Rebuild tournament projection and standings
        rebuild_tournament_projection(db, tournament_id)
        rebuild_tournament_standings(db, tournament_id)


@rabbitmq_service.event_handler(TournamentCompetitorDeletedV1)
def handle_tournament_competitor_deleted(event: TournamentCompetitorDeletedV1):
    """Handle tournament competitor deleted event."""
    tournament_id = event.data.tournament_id
    logger.info(
        "event_received",
        event_type="tournament.competitor.deleted",
        tournament_id=str(tournament_id),
    )

    with get_db() as db:
        query = db.query(TournamentCompetitor).filter(
            TournamentCompetitor.tournament_id == tournament_id,
            TournamentCompetitor.deleted_at.is_(None),
        )
        if event.data.competitor_entity_id is not None:
            query = query.filter(
                TournamentCompetitor.competitor_entity_id
                == event.data.competitor_entity_id
            )
        elif event.data.competitor_id is not None:
            query = query.filter(
                TournamentCompetitor.competitor_id == event.data.competitor_id
            )
        competitor = query.first()
        if not competitor:
            logger.warning(
                "tournament_competitor_not_found", tournament_id=str(tournament_id)
            )
            return
        competitor.deleted_at = datetime.utcnow()
        db.flush()
        # Rebuild tournament projection and standings
        rebuild_tournament_projection(db, tournament_id)
        rebuild_tournament_standings(db, tournament_id)


# ==================== Match Events ====================


@rabbitmq_service.event_handler(MatchCreatedV1)
def handle_match_created(event: MatchCreatedV1):
    """Handle match created event.

    Creates the Match record and any participants included in the event.
    """
    match_id = event.data.match_id
    logger.info("event_received", event_type="match.created", match_id=str(match_id))

    with get_db() as db:
        match = Match(
            match_id=match_id,
            tournament_id=event.data.tournament_id,
            location=event.data.location,
            status=MatchStatus(event.data.status),
            start_time=_parse_dt(event.data.start_time),
        )
        db.add(match)
        db.flush()

        for participant_data in event.data.participants:
            participant = MatchParticipant(
                match_id=match_id,
                participant_id=participant_data.participant_id,
                participant_type=ParticipantType(participant_data.participant_type),
                participant_entity_id=participant_data.participant_entity_id,
            )
            db.add(participant)

        db.flush()
        # Rebuild match projection and tournament projection (for match count)
        rebuild_match_projection(db, match_id)
        rebuild_tournament_projection(db, match.tournament_id)


@rabbitmq_service.event_handler(MatchUpdatedV1)
def handle_match_updated(event: MatchUpdatedV1):
    """Handle match updated event."""
    match_id = event.data.match_id
    logger.info("event_received", event_type="match.updated", match_id=str(match_id))

    with get_db() as db:
        match = db.query(Match).filter(Match.match_id == match_id).first()
        if not match:
            logger.warning("match_not_found", match_id=str(match_id))
            return
        if event.data.location is not None:
            match.location = event.data.location
        if event.data.start_time is not None:
            match.start_time = _parse_dt(event.data.start_time)
        if event.data.status is not None:
            old_status = match.status
            match.status = MatchStatus(event.data.status)
            # If match is newly completed, rebuild standings
            if old_status != MatchStatus.COMPLETED and match.status in [
                MatchStatus.COMPLETED,
                MatchStatus.FINISHED,
            ]:
                db.flush()
                rebuild_tournament_standings(db, match.tournament_id)
        match.updated_at = datetime.utcnow()
        db.flush()
        rebuild_match_projection(db, match_id)


@rabbitmq_service.event_handler(MatchDeletedV1)
def handle_match_deleted(event: MatchDeletedV1):
    """Handle match deleted event.

    Soft-deletes the match and cascades to participants.
    """
    match_id = event.data.match_id
    logger.info("event_received", event_type="match.deleted", match_id=str(match_id))

    with get_db() as db:
        match = db.query(Match).filter(Match.match_id == match_id).first()
        if not match:
            logger.warning("match_not_found", match_id=str(match_id))
            return
        now = datetime.utcnow()
        tournament_id = match.tournament_id
        match.deleted_at = now
        db.query(MatchParticipant).filter(
            MatchParticipant.match_id == match_id,
            MatchParticipant.removed_at.is_(None),
        ).update({"removed_at": now})
        db.flush()
        # Rebuild match projection and tournament projection (for match count)
        rebuild_match_projection(db, match_id)
        rebuild_tournament_projection(db, tournament_id)


@rabbitmq_service.event_handler(MatchParticipantAddedV1)
def handle_match_participant_added(event: MatchParticipantAddedV1):
    """Handle match participant added event."""
    match_id = event.data.match_id
    participant_id = event.data.participant_id
    logger.info(
        "event_received",
        event_type="match.participant.added",
        match_id=str(match_id),
        participant_id=str(participant_id),
    )

    with get_db() as db:
        participant = MatchParticipant(
            match_id=match_id,
            participant_id=participant_id,
            participant_type=ParticipantType(event.data.participant_type),
            participant_entity_id=event.data.participant_entity_id,
        )
        db.add(participant)
        db.flush()
        rebuild_match_projection(db, match_id)


@rabbitmq_service.event_handler(MatchParticipantRemovedV1)
def handle_match_participant_removed(event: MatchParticipantRemovedV1):
    """Handle match participant removed event."""
    match_id = event.data.match_id
    participant_id = event.data.participant_id
    logger.info(
        "event_received",
        event_type="match.participant.removed",
        match_id=str(match_id),
        participant_id=str(participant_id),
    )

    with get_db() as db:
        participant = (
            db.query(MatchParticipant)
            .filter(
                MatchParticipant.match_id == match_id,
                MatchParticipant.participant_id == participant_id,
                MatchParticipant.removed_at.is_(None),
            )
            .first()
        )
        if not participant:
            logger.warning(
                "match_participant_not_found",
                match_id=str(match_id),
                participant_id=str(participant_id),
            )
            return
        participant.removed_at = datetime.utcnow()
        db.flush()
        rebuild_match_projection(db, match_id)


@rabbitmq_service.event_handler(MatchResultUpdatedV1)
def handle_match_result_updated(event: MatchResultUpdatedV1):
    """Handle match result updated event.

    Upserts a MatchResult row for each result entry in the event.
    """
    match_id = event.data.match_id
    results = event.data.results
    logger.info(
        "event_received",
        event_type="match.result.updated",
        match_id=str(match_id),
        results_count=len(results),
    )

    with get_db() as db:
        for result_entry in results:
            participant_id = result_entry.participant_id
            existing = (
                db.query(MatchResult)
                .filter(
                    MatchResult.match_id == match_id,
                    MatchResult.participant_id == participant_id,
                )
                .first()
            )
            if existing:
                existing.score = result_entry.score
                existing.position = result_entry.position
                existing.results_metadata = result_entry.results_metadata
                existing.updated_at = datetime.utcnow()
            else:
                result = MatchResult(
                    match_id=match_id,
                    participant_id=participant_id,
                    score=result_entry.score,
                    position=result_entry.position,
                    results_metadata=result_entry.results_metadata,
                )
                db.add(result)

        db.flush()
        # Rebuild match projection and tournament standings
        match = db.query(Match).filter(Match.match_id == match_id).first()
        if match:
            rebuild_match_projection(db, match_id)
            rebuild_tournament_standings(db, match.tournament_id)


@rabbitmq_service.event_handler(MatchLineupAssignedV1)
def handle_match_lineup_assigned(event: MatchLineupAssignedV1):
    """Handle match lineup assigned event.

    Upserts MatchLineup rows for each player in the lineup.
    """
    match_id = event.data.match_id
    team_id = event.data.team_id
    logger.info(
        "event_received",
        event_type="match.lineup.assigned",
        match_id=str(match_id),
        team_id=str(team_id),
    )

    with get_db() as db:
        for player_entry in event.data.lineup:
            player_id = player_entry.player_id
            existing = (
                db.query(MatchLineup)
                .filter(
                    MatchLineup.match_id == match_id,
                    MatchLineup.team_id == team_id,
                    MatchLineup.player_id == player_id,
                )
                .first()
            )
            if existing:
                existing.jersey_number = player_entry.jersey_number
                existing.is_starter = player_entry.is_starter
            else:
                lineup_entry = MatchLineup(
                    match_id=match_id,
                    team_id=team_id,
                    player_id=player_id,
                    jersey_number=player_entry.jersey_number,
                    is_starter=player_entry.is_starter,
                )
                db.add(lineup_entry)


@rabbitmq_service.event_handler(MatchCommentAddedV1)
def handle_match_comment_added(event: MatchCommentAddedV1):
    """Handle match comment added event."""
    comment_id = event.data.comment_id
    match_id = event.data.match_id
    logger.info(
        "event_received",
        event_type="match.comment.added",
        match_id=str(match_id),
        comment_id=str(comment_id),
    )

    with get_db() as db:
        comment = MatchComment(
            comment_id=comment_id,
            match_id=match_id,
            message=event.data.message,
        )
        db.add(comment)
        db.flush()
        rebuild_match_projection(db, match_id)


@rabbitmq_service.event_handler(MatchCommentDeletedV1)
def handle_match_comment_deleted(event: MatchCommentDeletedV1):
    """Handle match comment deleted event."""
    comment_id = event.data.comment_id
    match_id = event.data.match_id
    logger.info(
        "event_received",
        event_type="match.comment.deleted",
        match_id=str(match_id),
        comment_id=str(comment_id),
    )

    with get_db() as db:
        comment = (
            db.query(MatchComment)
            .filter(
                MatchComment.comment_id == comment_id,
                MatchComment.deleted_at.is_(None),
            )
            .first()
        )
        if not comment:
            logger.warning("match_comment_not_found", comment_id=str(comment_id))
            return
        comment.deleted_at = datetime.now()
        db.flush()
        rebuild_match_projection(db, match_id)


# ==================== Ranking Events ====================


@rabbitmq_service.event_handler(RankingComputedV1)
def handle_ranking_computed(event: RankingComputedV1):
    """Handle ranking computed event from the ranking-service.

    Receives pre-computed points per course (and per modality) and rebuilds
    the GeneralRankingView projection, enriching each entry with course and
    nucleo names stored locally.
    """
    general_entries = event.data.general_ranking
    logger.info(
        "event_received",
        event_type="ranking.computed",
        general_entries=len(general_entries),
        modality_entries=len(event.data.modality_rankings),
    )

    with get_db() as db:
        from sqlalchemy.orm import joinedload

        # Replace the entire projection table atomically
        db.query(GeneralRankingView).delete()

        # Sort descending by points so we can assign ranks sequentially
        sorted_entries = sorted(general_entries, key=lambda e: e.points, reverse=True)

        rank = 1
        for idx, entry in enumerate(sorted_entries):
            # Handle ties — same rank for equal points
            if idx > 0 and entry.points == sorted_entries[idx - 1].points:
                current_rank = sorted_entries[idx - 1]._assigned_rank
            else:
                current_rank = rank

            # Stash rank on the entry so tied entries can reference it
            entry._assigned_rank = current_rank  # type: ignore[attr-defined]

            course = (
                db.query(Course)
                .options(joinedload(Course.nucleo))
                .filter(Course.course_id == entry.course_id)
                .first()
            )
            if not course:
                logger.warning(
                    "course_not_found_for_ranking",
                    course_id=str(entry.course_id),
                )
                rank += 1
                continue

            nucleo = course.nucleo

            ranking_view = GeneralRankingView(
                course_id=entry.course_id,
                course_name=course.name,
                course_abbreviation=course.abbreviation,
                nucleo_id=nucleo.nucleo_id if nucleo else None,
                nucleo_name=nucleo.name if nucleo else "",
                nucleo_abbreviation=nucleo.abbreviation if nucleo else "",
                points=entry.points,
                rank=current_rank,
                tournaments_participated=entry.tournaments_participated,
                updated_at=datetime.utcnow(),
            )
            db.add(ranking_view)

            rank += 1

        db.flush()
        logger.info(
            "general_ranking_view_updated",
            entries=len(sorted_entries),
        )
