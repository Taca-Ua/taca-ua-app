"""
Projection Repository Layer.

This module is responsible for:
- Clearing all projection tables safely
- Rebuilding projection tables from snapshot data
- Managing transactional integrity during rebuild

Architecture Note:
- This layer directly interacts with the database
- All operations should be transactional when possible
- Clear operations must be safe and preserve schema
"""

from typing import List

from sqlalchemy import text
from sqlalchemy.orm import Session
from taca_snapshots.matches import (
    MatchCommentSnapshotItem,
    MatchLineupSnapshotItem,
    MatchParticipantSnapshotItem,
    MatchResultSnapshotItem,
    MatchSnapshotItem,
)
from taca_snapshots.modalities import (
    CourseSnapshotItem,
    ModalitySnapshotItem,
    ModalityTypeSnapshotItem,
    NucleoSnapshotItem,
    StaffSnapshotItem,
    StudentSnapshotItem,
    TeamPlayerSnapshotItem,
    TeamSnapshotItem,
)
from taca_snapshots.tournaments import (
    TournamentCompetitorSnapshotItem,
    TournamentRankingPositionSnapshotItem,
    TournamentSnapshotItem,
)

from ..logger import logger
from ..models import (
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
from ..utils import (
    rebuild_general_ranking,
    rebuild_match_projection,
    rebuild_student_projection,
    rebuild_team_projection,
    rebuild_tournament_projection,
    rebuild_tournament_standings,
)
from .dto import CompleteSnapshot


class ProjectionRepository:
    """
    Repository for managing read model projection tables.

    This repository provides methods to safely clear and rebuild
    all projection tables from snapshot data.
    """

    def __init__(self, db_session: Session):
        """
        Initialize repository with database session.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def clear_all_projections(self) -> None:
        """
        Clear all projection tables in the correct order.

        This method deletes all data from projection tables while
        respecting foreign key constraints. Tables are cleared in
        reverse dependency order.

        IMPORTANT: This is a destructive operation. It should only be
        called during a rebuild when event consumption is paused.
        """
        logger.info("projection_clear_started")

        try:
            # Clear tables in reverse dependency order to respect foreign keys
            # Order matters!

            # 0. Clear materialized views first (no dependencies, but depend on core tables)
            self.db.query(GeneralRankingView).delete()
            self.db.query(TournamentStandingsView).delete()
            self.db.query(MatchDetailView).delete()
            self.db.query(TournamentDetailView).delete()
            self.db.query(StudentDetailView).delete()
            self.db.query(TeamDetailView).delete()

            # 1. Clear match-related dependent tables first
            self.db.query(MatchComment).delete()
            self.db.query(MatchLineup).delete()
            self.db.query(MatchResult).delete()
            self.db.query(MatchParticipant).delete()
            self.db.query(Match).delete()

            # 2. Clear tournament-related tables
            self.db.query(TournamentCompetitor).delete()
            self.db.query(TournamentRanking).delete()
            self.db.query(Tournament).delete()

            # 3. Clear team and player tables
            self.db.query(TeamPlayer).delete()
            self.db.query(Team).delete()

            # 4. Clear student and staff tables
            self.db.query(Student).delete()
            self.db.query(Staff).delete()

            # 5. Clear modality tables
            self.db.query(Modality).delete()
            self.db.query(ModalityType).delete()

            # 6. Clear course and nucleo tables
            self.db.query(Course).delete()
            self.db.query(Nucleo).delete()

            # Commit the transaction
            self.db.commit()

            logger.info("projection_clear_success")

        except Exception as e:
            self.db.rollback()
            logger.error("projection_clear_failed", error=str(e))
            raise

    def rebuild_from_snapshot(self, snapshot: CompleteSnapshot) -> int:
        """
        Rebuild all projection tables from snapshot data.

        This method populates projection tables in the correct order,
        respecting foreign key constraints.

        Args:
            snapshot: Complete snapshot data from all services

        Returns:
            Total number of records inserted

        Raises:
            Exception: If rebuild fails (transaction will be rolled back)
        """
        logger.info("projection_rebuild_started")

        try:
            total_records = 0

            # Rebuild in correct dependency order

            # 1. Rebuild base reference data (no dependencies)
            if snapshot.modalities:
                total_records += self._rebuild_nucleos(snapshot.modalities.nucleos)
                total_records += self._rebuild_courses(snapshot.modalities.courses)
                total_records += self._rebuild_modality_types(
                    snapshot.modalities.modality_types
                )
                total_records += self._rebuild_modalities(
                    snapshot.modalities.modalities
                )
                total_records += self._rebuild_students(snapshot.modalities.students)
                total_records += self._rebuild_staff(snapshot.modalities.staff)
                total_records += self._rebuild_teams(snapshot.modalities.teams)
                total_records += self._rebuild_team_players(
                    snapshot.modalities.team_players
                )

            # 2. Rebuild tournaments (depends on modalities and teams)
            if snapshot.tournament:
                total_records += self._rebuild_tournaments(
                    snapshot.tournament.tournaments
                )
                total_records += self._rebuild_tournament_competitors(
                    snapshot.tournament.competitors
                )
                total_records += self._rebuild_tournament_rankings(
                    snapshot.tournament.rankings
                )

            # 3. Rebuild matches (depends on tournaments and teams)
            if snapshot.matches:
                total_records += self._rebuild_matches(snapshot.matches.matches)
                total_records += self._rebuild_match_participants(
                    snapshot.matches.participants
                )
                total_records += self._rebuild_match_results(snapshot.matches.results)
                total_records += self._rebuild_match_lineups(snapshot.matches.lineups)
                total_records += self._rebuild_match_comments(snapshot.matches.comments)

            # Note: Ranking data can be rebuilt here if needed
            # if snapshot.ranking:
            #     total_records += self._rebuild_rankings(snapshot.ranking.rankings)

            # Commit the core tables first
            self.db.commit()

            # 4. Rebuild materialized views from core tables
            logger.info("materialized_views_rebuild_started")
            materialized_records = self._rebuild_materialized_views()
            total_records += materialized_records
            logger.info(
                "materialized_views_rebuild_success",
                materialized_records=materialized_records,
            )

            # Final commit
            self.db.commit()

            logger.info("projection_rebuild_success", total_records=total_records)

            return total_records

        except Exception as e:
            self.db.rollback()
            logger.error("projection_rebuild_failed", error=str(e))
            raise

    # ==================== Private Rebuild Methods ====================
    # Each method rebuilds a specific table from snapshot data

    def _rebuild_nucleos(self, nucleos: List[NucleoSnapshotItem]) -> int:
        """Rebuild Nucleo table from typed snapshot items."""
        if not nucleos:
            return 0

        for item in nucleos:
            nucleo = Nucleo(
                nucleo_id=item.id,
                name=item.name,
                abbreviation=item.abbreviation,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            self.db.add(nucleo)

        self.db.flush()
        logger.debug("projection_rebuilt", table="nucleos", count=len(nucleos))
        return len(nucleos)

    def _rebuild_courses(self, courses: List[CourseSnapshotItem]) -> int:
        """Rebuild Course table from typed snapshot items."""
        if not courses:
            return 0

        for item in courses:
            course = Course(
                course_id=item.id,
                nucleo_id=item.nucleo_id,
                name=item.name,
                abbreviation=item.abbreviation,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            self.db.add(course)

        self.db.flush()
        logger.debug("projection_rebuilt", table="courses", count=len(courses))
        return len(courses)

    def _rebuild_modality_types(
        self, modality_types: List[ModalityTypeSnapshotItem]
    ) -> int:
        """Rebuild ModalityType table from typed snapshot items."""
        if not modality_types:
            return 0

        for item in modality_types:
            modality_type = ModalityType(
                modality_type_id=item.id,
                name=item.name,
                description=item.description,
                escaloes=item.escaloes,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            self.db.add(modality_type)

        self.db.flush()
        logger.debug(
            "projection_rebuilt", table="modality_types", count=len(modality_types)
        )
        return len(modality_types)

    def _rebuild_modalities(self, modalities: List[ModalitySnapshotItem]) -> int:
        """Rebuild Modality table from typed snapshot items."""
        if not modalities:
            return 0

        for item in modalities:
            modality = Modality(
                modality_id=item.id,
                modality_type_id=item.modality_type_id,
                name=item.name,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            self.db.add(modality)

        self.db.flush()
        logger.debug("projection_rebuilt", table="modalities", count=len(modalities))
        return len(modalities)

    def _rebuild_students(self, students: List[StudentSnapshotItem]) -> int:
        """Rebuild Student table from typed snapshot items."""
        if not students:
            return 0

        for item in students:
            student = Student(
                student_id=item.id,
                course_id=item.course_id,
                student_number=item.student_number,
                full_name=item.full_name,
                is_member=item.is_member,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            self.db.add(student)

        self.db.flush()
        logger.debug("projection_rebuilt", table="students", count=len(students))
        return len(students)

    def _rebuild_staff(self, staff: List[StaffSnapshotItem]) -> int:
        """Rebuild Staff table from typed snapshot items."""
        if not staff:
            return 0

        for item in staff:
            staff_member = Staff(
                staff_id=item.id,
                full_name=item.full_name,
                staff_number=item.staff_number,
                contact=item.contact,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            self.db.add(staff_member)

        self.db.flush()
        logger.debug("projection_rebuilt", table="staff", count=len(staff))
        return len(staff)

    def _rebuild_teams(self, teams: List[TeamSnapshotItem]) -> int:
        """Rebuild Team table from typed snapshot items."""
        if not teams:
            return 0

        for item in teams:
            team = Team(
                team_id=item.id,
                modality_id=item.modality_id,
                course_id=item.course_id,
                name=item.name,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            self.db.add(team)

        self.db.flush()
        logger.debug("projection_rebuilt", table="teams", count=len(teams))
        return len(teams)

    def _rebuild_team_players(self, team_players: List[TeamPlayerSnapshotItem]) -> int:
        """Rebuild TeamPlayer table from typed snapshot items."""
        if not team_players:
            return 0

        for item in team_players:
            # TeamPlayer has auto-increment id, so we don't pass it
            team_player = TeamPlayer(
                team_id=item.team_id,
                student_id=item.student_id,
            )
            self.db.add(team_player)

        self.db.flush()
        logger.debug(
            "projection_rebuilt", table="team_players", count=len(team_players)
        )
        return len(team_players)

    def _rebuild_tournaments(self, tournaments: List[TournamentSnapshotItem]) -> int:
        """Rebuild Tournament table from typed snapshot items."""
        if not tournaments:
            return 0

        for item in tournaments:
            tournament = Tournament(
                tournament_id=item.id,
                modality_id=item.modality_id,
                name=item.name,
                start_date=item.start_date,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
                finished_at=item.finished_at,
            )
            self.db.add(tournament)

        self.db.flush()
        logger.debug("projection_rebuilt", table="tournaments", count=len(tournaments))
        return len(tournaments)

    def _rebuild_tournament_competitors(
        self, competitors: List[TournamentCompetitorSnapshotItem]
    ) -> int:
        """Rebuild TournamentCompetitor table from typed snapshot items."""
        if not competitors:
            return 0

        for item in competitors:
            # Map team_id or athlete_id to competitor_entity_id
            competitor_entity_id = item.team_id or item.athlete_id

            competitor = TournamentCompetitor(
                competitor_id=item.id,
                tournament_id=item.tournament_id,
                competitor_type=item.competitor_type,
                competitor_entity_id=competitor_entity_id,
                added_at=item.created_at,
            )
            self.db.add(competitor)

        self.db.flush()
        logger.debug(
            "projection_rebuilt", table="tournament_competitors", count=len(competitors)
        )
        return len(competitors)

    def _rebuild_tournament_rankings(
        self, rankings: List[TournamentRankingPositionSnapshotItem]
    ) -> int:
        """Rebuild TournamentRanking table from typed snapshot items."""
        if not rankings:
            return 0

        for item in rankings:
            ranking = TournamentRanking(
                tournament_id=item.tournament_id,
                competitor_id=item.competitor_id,
                position=item.position,
                created_at=item.created_at,
            )
            self.db.add(ranking)

        self.db.flush()
        logger.debug(
            "projection_rebuilt", table="tournament_rankings", count=len(rankings)
        )
        return len(rankings)

    def _rebuild_matches(self, matches: List[MatchSnapshotItem]) -> int:
        """Rebuild Match table from typed snapshot items."""
        if not matches:
            return 0

        for item in matches:
            match = Match(
                match_id=item.match_id,
                tournament_id=item.tournament_id,
                location=item.location,
                status=item.status,
                start_time=item.start_time,
                created_at=item.created_at,
                updated_at=item.updated_at,
                deleted_at=item.deleted_at,
            )
            self.db.add(match)

        self.db.flush()
        logger.debug("projection_rebuilt", table="matches", count=len(matches))
        return len(matches)

    def _rebuild_match_participants(
        self, participants: List[MatchParticipantSnapshotItem]
    ) -> int:
        """Rebuild MatchParticipant table from typed snapshot items."""
        if not participants:
            return 0

        for item in participants:
            # MatchParticipant has auto-increment id, so we don't pass it
            participant = MatchParticipant(
                match_id=item.match_id,
                participant_id=item.participant_id,
                participant_type=item.participant_type,
                participant_entity_id=item.participant_entity_id,
                added_at=item.added_at,
                removed_at=item.removed_at,
            )
            self.db.add(participant)

        self.db.flush()
        logger.debug(
            "projection_rebuilt", table="match_participants", count=len(participants)
        )
        return len(participants)

    def _rebuild_match_results(self, results: List[MatchResultSnapshotItem]) -> int:
        """Rebuild MatchResult table from typed snapshot items."""
        if not results:
            return 0

        for item in results:
            # MatchResult has auto-increment id, so we don't pass it
            result = MatchResult(
                match_id=item.match_id,
                participant_id=item.participant_id,
                score=item.score,
                position=item.position,
                results_metadata=item.results_metadata,
                updated_at=item.updated_at,
            )
            self.db.add(result)

        self.db.flush()
        logger.debug("projection_rebuilt", table="match_results", count=len(results))
        return len(results)

    def _rebuild_match_lineups(self, lineups: List[MatchLineupSnapshotItem]) -> int:
        """Rebuild MatchLineup table from typed snapshot items."""
        if not lineups:
            return 0

        for item in lineups:
            # MatchLineup has auto-increment id, so we don't pass it
            lineup = MatchLineup(
                match_id=item.match_id,
                team_id=item.team_id,
                player_id=item.player_id,
                jersey_number=item.jersey_number,
                is_starter=item.is_starter,
                assigned_at=item.assigned_at,
            )
            self.db.add(lineup)

        self.db.flush()
        logger.debug("projection_rebuilt", table="match_lineups", count=len(lineups))
        return len(lineups)

    def _rebuild_match_comments(self, comments: List[MatchCommentSnapshotItem]) -> int:
        """Rebuild MatchComment table from typed snapshot items."""
        if not comments:
            return 0

        for item in comments:
            comment = MatchComment(
                comment_id=item.comment_id,
                match_id=item.match_id,
                message=item.message,
                created_at=item.created_at,
                deleted_at=item.deleted_at,
            )
            self.db.add(comment)

        self.db.flush()
        logger.debug("projection_rebuilt", table="match_comments", count=len(comments))
        return len(comments)

    def _rebuild_materialized_views(self) -> int:
        """
        Rebuild all materialized views from core tables.

        This method is called after core tables are populated from snapshots.
        It rebuilds denormalized/optimized views for query performance.

        Returns:
            Number of materialized view records created
        """
        total_records = 0

        try:
            # Rebuild team detail views
            teams = self.db.query(Team.team_id).filter(Team.deleted_at.is_(None)).all()
            for (team_id,) in teams:
                rebuild_team_projection(self.db, team_id)
                total_records += 1
            logger.debug(
                "materialized_view_rebuilt", view="team_details", count=len(teams)
            )

            # Rebuild student detail views
            students = (
                self.db.query(Student.student_id)
                .filter(Student.deleted_at.is_(None))
                .all()
            )
            for (student_id,) in students:
                rebuild_student_projection(self.db, student_id)
                total_records += 1
            logger.debug(
                "materialized_view_rebuilt", view="student_details", count=len(students)
            )

            # Rebuild tournament detail views
            tournaments = (
                self.db.query(Tournament.tournament_id)
                .filter(Tournament.deleted_at.is_(None))
                .all()
            )
            for (tournament_id,) in tournaments:
                rebuild_tournament_projection(self.db, tournament_id)
                total_records += 1
            logger.debug(
                "materialized_view_rebuilt",
                view="tournament_details",
                count=len(tournaments),
            )

            # Rebuild match detail views
            matches = (
                self.db.query(Match.match_id).filter(Match.deleted_at.is_(None)).all()
            )
            for (match_id,) in matches:
                rebuild_match_projection(self.db, match_id)
                total_records += 1
            logger.debug(
                "materialized_view_rebuilt", view="match_details", count=len(matches)
            )

            # Rebuild tournament standings
            for (tournament_id,) in tournaments:
                rebuild_tournament_standings(self.db, tournament_id)
                # Standings records counted separately as they're per-competitor
            standings_count = self.db.query(TournamentStandingsView).count()
            total_records += standings_count
            logger.debug(
                "materialized_view_rebuilt",
                view="tournament_standings",
                count=standings_count,
            )

            # Rebuild general ranking
            rebuild_general_ranking(self.db)
            general_ranking_count = self.db.query(GeneralRankingView).count()
            total_records += general_ranking_count
            logger.debug(
                "materialized_view_rebuilt",
                view="general_ranking",
                count=general_ranking_count,
            )

            # Flush to ensure all writes are done
            self.db.flush()

        except Exception as e:
            logger.error("materialized_views_rebuild_failed", error=str(e))
            raise

        return total_records

    def reset_sequences(self) -> None:
        """
        Reset all database sequences to match the current max IDs.

        This ensures that new inserts after rebuild don't conflict
        with existing IDs.

        Note: Only needed for tables with auto-increment integer IDs.
        Most tables use UUID primary keys and don't have sequences.
        This is PostgreSQL-specific. Adjust for other databases.
        """
        logger.info("projection_reset_sequences_started")

        try:
            # Only tables with auto-increment integer IDs need sequence resets
            # Most tables use UUID primary keys which don't have sequences
            tables_with_sequences = [
                ("public_read.team_players", "id"),
                ("public_read.match_participants", "id"),
                ("public_read.match_results", "id"),
                ("public_read.match_lineups", "id"),
                ("public_read.mv_tournament_standings", "id"),  # Materialized view
                ("public_read.mv_general_ranking", "id"),  # Materialized view
            ]

            for table_name, id_column in tables_with_sequences:
                # Reset sequence to max ID + 1
                sql = text(
                    f"""
                    SELECT setval(
                        pg_get_serial_sequence('{table_name}', '{id_column}'),
                        COALESCE((SELECT MAX({id_column}) FROM {table_name}), 1),
                        true
                    )
                    """
                )
                self.db.execute(sql)

            self.db.commit()
            logger.info("projection_reset_sequences_success")

        except Exception as e:
            self.db.rollback()
            logger.error("projection_reset_sequences_failed", error=str(e))
            raise
