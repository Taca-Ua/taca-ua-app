"""
Read-model-updater rebuild controller.

Exposes the standard internal rebuild endpoints and the
:class:`ReadModelRebuildService` that repopulates all projection tables
from upstream domain service snapshots.

Exposed endpoints (all require ``X-INTERNAL-TOKEN``):
- POST /internal/rebuild
- GET  /internal/rebuild/status
- POST /internal/rebuild/pause
- POST /internal/rebuild/resume
"""

from typing import Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import joinedload
from taca_rebuild import BaseRebuildService, make_rebuild_router
from taca_snapshots.matches import (
    MatchCommentSnapshotItem,
    MatchesSnapshotResponse,
    MatchLineupSnapshotItem,
    MatchParticipantSnapshotItem,
    MatchResultSnapshotItem,
    MatchSnapshotItem,
)
from taca_snapshots.modalities import (
    CourseSnapshotItem,
    ModalitiesSnapshotResponse,
    ModalitySnapshotItem,
    ModalityTypeSnapshotItem,
    NucleoSnapshotItem,
    StaffSnapshotItem,
    StudentSnapshotItem,
    TeamPlayerSnapshotItem,
    TeamSnapshotItem,
)
from taca_snapshots.ranking import GeneralRankingSnapshotItem, RankingSnapshotResponse
from taca_snapshots.tournaments import (
    TournamentCompetitorSnapshotItem,
    TournamentRankingPositionSnapshotItem,
    TournamentSnapshotItem,
    TournamentsSnapshotResponse,
)

from .config import Config
from .database import get_db_session
from .events import rabbitmq_service
from .logger import logger
from .models import (
    Course,
    GeneralRankingView,
    Match,
    MatchComment,
    MatchDetailView,
    MatchLineup,
    MatchParticipant,
    MatchResult,
    Modality,
    ModalityType,
    Nucleo,
    Staff,
    Student,
    StudentDetailView,
    Team,
    TeamDetailView,
    TeamPlayer,
    Tournament,
    TournamentCompetitor,
    TournamentDetailView,
    TournamentRanking,
    TournamentStandingsView,
)
from .utils import (
    rebuild_match_projection,
    rebuild_student_projection,
    rebuild_team_projection,
    rebuild_tournament_projection,
    rebuild_tournament_standings,
)


class ReadModelRebuildService(BaseRebuildService):
    @property
    def snapshot_sources(self) -> Dict[str, str]:
        return {
            "matches": f"{Config.MATCHES_SERVICE_URL}/internal/snapshot",
            "tournament": f"{Config.TOURNAMENT_SERVICE_URL}/internal/snapshot",
            "modalities": f"{Config.MODALITIES_SERVICE_URL}/internal/snapshot",
            "ranking": f"{Config.RANKING_SERVICE_URL}/internal/snapshot",
        }

    def clear_tables(self) -> None:
        logger.info("projections_clearing")
        # Clear in reverse dependency order to respect foreign keys
        self.db.query(GeneralRankingView).delete()
        self.db.query(TournamentStandingsView).delete()
        self.db.query(MatchDetailView).delete()
        self.db.query(TournamentDetailView).delete()
        self.db.query(StudentDetailView).delete()
        self.db.query(TeamDetailView).delete()
        self.db.query(MatchComment).delete()
        self.db.query(MatchLineup).delete()
        self.db.query(MatchResult).delete()
        self.db.query(MatchParticipant).delete()
        self.db.query(Match).delete()
        self.db.query(TournamentCompetitor).delete()
        self.db.query(TournamentRanking).delete()
        self.db.query(Tournament).delete()
        self.db.query(TeamPlayer).delete()
        self.db.query(Team).delete()
        self.db.query(Student).delete()
        self.db.query(Staff).delete()
        self.db.query(Modality).delete()
        self.db.query(ModalityType).delete()
        self.db.query(Course).delete()
        self.db.query(Nucleo).delete()
        self.db.commit()
        logger.info("projections_cleared")

    def rebuild_from_snapshots(self, raw: Dict[str, Optional[dict]]) -> int:
        mod = (
            ModalitiesSnapshotResponse(**raw["modalities"])
            if raw.get("modalities")
            else None
        )
        tour = (
            TournamentsSnapshotResponse(**raw["tournament"])
            if raw.get("tournament")
            else None
        )
        matches = (
            MatchesSnapshotResponse(**raw["matches"]) if raw.get("matches") else None
        )
        ranking = (
            RankingSnapshotResponse(**raw["ranking"]) if raw.get("ranking") else None
        )

        logger.info("projections_rebuilding")
        total = 0

        if mod:
            total += self._rebuild_nucleos(mod.nucleos)
            total += self._rebuild_courses(mod.courses)
            total += self._rebuild_modality_types(mod.modality_types)
            total += self._rebuild_modalities(mod.modalities)
            total += self._rebuild_students(mod.students)
            total += self._rebuild_staff(mod.staff)
            total += self._rebuild_teams(mod.teams)
            total += self._rebuild_team_players(mod.team_players)

        if tour:
            total += self._rebuild_tournaments(tour.tournaments)
            total += self._rebuild_tournament_competitors(tour.competitors)
            total += self._rebuild_tournament_rankings(tour.ranking_positions)

        if matches:
            total += self._rebuild_matches(matches.matches)
            total += self._rebuild_match_participants(matches.participants)
            total += self._rebuild_match_results(matches.results)
            total += self._rebuild_match_lineups(matches.lineups)
            total += self._rebuild_match_comments(matches.comments)

        self.db.commit()
        total += self._rebuild_materialized_views()

        if ranking:
            total += self._rebuild_general_ranking_from_snapshot(
                ranking.general_rankings
            )

        self.db.commit()
        self._reset_sequences()

        logger.info("projections_rebuilt", records_processed=total)
        return total

    def get_status(self) -> dict:
        try:
            return {
                "core_projections": {
                    "matches": self.db.query(Match).count(),
                    "tournaments": self.db.query(Tournament).count(),
                    "teams": self.db.query(Team).count(),
                    "students": self.db.query(Student).count(),
                    "modalities": self.db.query(Modality).count(),
                },
                "materialized_views": {
                    "team_details": self.db.query(TeamDetailView).count(),
                    "student_details": self.db.query(StudentDetailView).count(),
                    "tournament_details": self.db.query(TournamentDetailView).count(),
                    "match_details": self.db.query(MatchDetailView).count(),
                    "tournament_standings": self.db.query(
                        TournamentStandingsView
                    ).count(),
                },
                "event_consumption_paused": getattr(
                    self.rabbitmq_svc, "is_paused", lambda: False
                )(),
            }
        except Exception as exc:
            logger.error("rebuild_status_check_failed", error=str(exc))
            return {"error": "Failed to retrieve status", "message": str(exc)}

    # ------------------------------------------------------------------
    # Private helpers — one per table
    # ------------------------------------------------------------------

    def _rebuild_nucleos(self, nucleos: List[NucleoSnapshotItem]) -> int:
        if not nucleos:
            return 0
        for item in nucleos:
            self.db.add(
                Nucleo(
                    nucleo_id=item.id,
                    name=item.name,
                    abbreviation=item.abbreviation,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )
        self.db.flush()
        return len(nucleos)

    def _rebuild_courses(self, courses: List[CourseSnapshotItem]) -> int:
        if not courses:
            return 0
        for item in courses:
            self.db.add(
                Course(
                    course_id=item.id,
                    nucleo_id=item.nucleo_id,
                    name=item.name,
                    abbreviation=item.abbreviation,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )
        self.db.flush()
        return len(courses)

    def _rebuild_modality_types(
        self, modality_types: List[ModalityTypeSnapshotItem]
    ) -> int:
        if not modality_types:
            return 0
        for item in modality_types:
            self.db.add(
                ModalityType(
                    modality_type_id=item.id,
                    name=item.name,
                    description=item.description,
                    escaloes=[
                        {
                            "min_participants": e.min_participants,
                            "max_participants": e.max_participants,
                            "points": e.points,
                        }
                        for e in item.escaloes or []
                    ],
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )
        self.db.flush()
        return len(modality_types)

    def _rebuild_modalities(self, modalities: List[ModalitySnapshotItem]) -> int:
        if not modalities:
            return 0
        for item in modalities:
            self.db.add(
                Modality(
                    modality_id=item.id,
                    modality_type_id=item.modality_type_id,
                    name=item.name,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )
        self.db.flush()
        return len(modalities)

    def _rebuild_students(self, students: List[StudentSnapshotItem]) -> int:
        if not students:
            return 0
        for item in students:
            self.db.add(
                Student(
                    student_id=item.id,
                    course_id=item.course_id,
                    student_number=item.student_number,
                    full_name=item.full_name,
                    is_member=item.is_member,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )
        self.db.flush()
        return len(students)

    def _rebuild_staff(self, staff: List[StaffSnapshotItem]) -> int:
        if not staff:
            return 0
        for item in staff:
            self.db.add(
                Staff(
                    staff_id=item.id,
                    full_name=item.full_name,
                    staff_number=item.staff_number,
                    contact=item.contact,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )
        self.db.flush()
        return len(staff)

    def _rebuild_teams(self, teams: List[TeamSnapshotItem]) -> int:
        if not teams:
            return 0
        for item in teams:
            self.db.add(
                Team(
                    team_id=item.id,
                    modality_id=item.modality_id,
                    course_id=item.course_id,
                    name=item.name,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )
        self.db.flush()
        return len(teams)

    def _rebuild_team_players(self, team_players: List[TeamPlayerSnapshotItem]) -> int:
        if not team_players:
            return 0
        for item in team_players:
            self.db.add(TeamPlayer(team_id=item.team_id, student_id=item.student_id))
        self.db.flush()
        return len(team_players)

    def _rebuild_tournaments(self, tournaments: List[TournamentSnapshotItem]) -> int:
        if not tournaments:
            return 0
        for item in tournaments:
            self.db.add(
                Tournament(
                    tournament_id=item.id,
                    modality_id=item.modality_id,
                    name=item.name,
                    start_date=item.start_date,
                    status=item.status,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                    finished_at=item.finished_at,
                )
            )
        self.db.flush()
        return len(tournaments)

    def _rebuild_tournament_competitors(
        self, competitors: List[TournamentCompetitorSnapshotItem]
    ) -> int:
        if not competitors:
            return 0
        for item in competitors:
            self.db.add(
                TournamentCompetitor(
                    competitor_id=item.id,
                    tournament_id=item.tournament_id,
                    competitor_type=item.competitor_type,
                    competitor_entity_id=item.team_id or item.athlete_id,
                    added_at=item.created_at,
                )
            )
        self.db.flush()
        return len(competitors)

    def _rebuild_tournament_rankings(
        self, rankings: List[TournamentRankingPositionSnapshotItem]
    ) -> int:
        if not rankings:
            return 0
        for item in rankings:
            self.db.add(
                TournamentRanking(
                    tournament_id=item.tournament_id,
                    competitor_id=item.competitor_id,
                    position=item.position,
                    created_at=item.created_at,
                )
            )
        self.db.flush()
        return len(rankings)

    def _rebuild_matches(self, matches: List[MatchSnapshotItem]) -> int:
        if not matches:
            return 0
        for item in matches:
            self.db.add(
                Match(
                    match_id=item.match_id,
                    tournament_id=item.tournament_id,
                    location=item.location,
                    status=item.status,
                    start_time=item.start_time,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                    deleted_at=item.deleted_at,
                )
            )
        self.db.flush()
        return len(matches)

    def _rebuild_match_participants(
        self, participants: List[MatchParticipantSnapshotItem]
    ) -> int:
        if not participants:
            return 0
        for item in participants:
            self.db.add(
                MatchParticipant(
                    match_id=item.match_id,
                    participant_id=item.participant_id,
                    participant_type=item.participant_type,
                    participant_entity_id=item.participant_entity_id,
                    added_at=item.added_at,
                    removed_at=item.removed_at,
                )
            )
        self.db.flush()
        return len(participants)

    def _rebuild_match_results(self, results: List[MatchResultSnapshotItem]) -> int:
        if not results:
            return 0
        for item in results:
            self.db.add(
                MatchResult(
                    match_id=item.match_id,
                    participant_id=item.participant_id,
                    score=item.score,
                    position=item.position,
                    results_metadata=item.results_metadata,
                    updated_at=item.updated_at,
                )
            )
        self.db.flush()
        return len(results)

    def _rebuild_match_lineups(self, lineups: List[MatchLineupSnapshotItem]) -> int:
        if not lineups:
            return 0
        for item in lineups:
            self.db.add(
                MatchLineup(
                    match_id=item.match_id,
                    team_id=item.team_id,
                    player_id=item.player_id,
                    jersey_number=item.jersey_number,
                    is_starter=item.is_starter,
                    assigned_at=item.assigned_at,
                )
            )
        self.db.flush()
        return len(lineups)

    def _rebuild_match_comments(self, comments: List[MatchCommentSnapshotItem]) -> int:
        if not comments:
            return 0
        for item in comments:
            self.db.add(
                MatchComment(
                    comment_id=item.comment_id,
                    match_id=item.match_id,
                    message=item.message,
                    created_at=item.created_at,
                    deleted_at=item.deleted_at,
                )
            )
        self.db.flush()
        return len(comments)

    def _rebuild_general_ranking_from_snapshot(
        self, entries: List[GeneralRankingSnapshotItem]
    ) -> int:
        from datetime import datetime

        if not entries:
            return 0
        sorted_entries = sorted(entries, key=lambda e: e.points, reverse=True)
        added = 0
        prev_points: Optional[int] = None
        current_rank = 0
        for idx, item in enumerate(sorted_entries):
            if item.points != prev_points:
                current_rank = idx + 1
            prev_points = item.points
            course = (
                self.db.query(Course)
                .options(joinedload(Course.nucleo))
                .filter(Course.course_id == item.course_id)
                .first()
            )
            if not course:
                logger.warning(
                    "ranking_rebuild_course_not_found", course_id=str(item.course_id)
                )
                current_rank = idx + 1
                continue
            nucleo = course.nucleo
            print(
                f"Adding ranking entry: course_id={course.course_id}, course_name={course.name}, points={item.points}, rank={current_rank}"
            )
            self.db.add(
                GeneralRankingView(
                    course_id=item.course_id,
                    course_name=course.name,
                    course_abbreviation=course.abbreviation,
                    nucleo_id=nucleo.nucleo_id if nucleo else None,
                    nucleo_name=nucleo.name if nucleo else "",
                    nucleo_abbreviation=nucleo.abbreviation if nucleo else "",
                    points=item.points,
                    rank=current_rank,
                    tournaments_participated=item.tournaments_participated,
                    updated_at=datetime.utcnow(),
                )
            )
            added += 1
        self.db.flush()
        return added

    def _rebuild_materialized_views(self) -> int:
        total = 0

        teams = self.db.query(Team.team_id).filter(Team.deleted_at.is_(None)).all()
        for (team_id,) in teams:
            rebuild_team_projection(self.db, team_id)
            total += 1

        students = (
            self.db.query(Student.student_id).filter(Student.deleted_at.is_(None)).all()
        )
        for (student_id,) in students:
            rebuild_student_projection(self.db, student_id)
            total += 1

        tournaments = (
            self.db.query(Tournament.tournament_id)
            .filter(Tournament.deleted_at.is_(None))
            .all()
        )
        for (tournament_id,) in tournaments:
            rebuild_tournament_projection(self.db, tournament_id)
            total += 1

        matches = self.db.query(Match.match_id).filter(Match.deleted_at.is_(None)).all()
        for (match_id,) in matches:
            rebuild_match_projection(self.db, match_id)
            total += 1

        for (tournament_id,) in tournaments:
            rebuild_tournament_standings(self.db, tournament_id)
        total += self.db.query(TournamentStandingsView).count()

        self.db.flush()
        return total

    def _reset_sequences(self) -> None:
        tables_with_sequences = [
            ("public_read.team_players", "id"),
            ("public_read.match_participants", "id"),
            ("public_read.match_results", "id"),
            ("public_read.match_lineups", "id"),
            ("public_read.mv_tournament_standings", "id"),
            ("public_read.mv_general_ranking", "id"),
        ]
        for table_name, id_column in tables_with_sequences:
            self.db.execute(
                text(
                    f"SELECT setval(pg_get_serial_sequence('{table_name}', '{id_column}'),"
                    f" COALESCE((SELECT MAX({id_column}) FROM {table_name}), 1), true)"
                )
            )
        self.db.commit()


router = make_rebuild_router(
    service_cls=ReadModelRebuildService,
    rabbitmq_svc=rabbitmq_service,
    get_db=get_db_session,
    internal_token=Config.INTERNAL_API_TOKEN,
    timeout=Config.SNAPSHOT_REQUEST_TIMEOUT,
    max_retries=Config.SNAPSHOT_MAX_RETRIES,
)
