"""
Projection rebuild utilities for materialized views.

These functions query core tables and update materialized views.
They should be called after core table updates (from events or snapshot rebuilds).
"""

from typing import Dict, List
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .models import (
    Course,
    Match,
    MatchComment,
    MatchDetailView,
    MatchParticipant,
    MatchResult,
    Modality,
    Nucleo,
    Season,
    Student,
    StudentDetailView,
    Team,
    TeamDetailView,
    TeamPlayer,
    Tournament,
    TournamentCompetitor,
    TournamentDetailView,
    TournamentStandingsView,
)

# ==================== Team Detail View ====================


def rebuild_team_projection(session: Session, team_id: UUID) -> None:
    """
    Rebuild mv_team_details for a specific team.

    Dependencies: Team, Course, Nucleo, Modality, ModalityType, TeamPlayer

    Call when:
    - Team created/updated/deleted
    - Course updated
    - Nucleo updated
    - Modality updated
    - ModalityType updated
    - TeamPlayer added/removed
    """
    # Load canonical state with relationships
    team = (
        session.query(Team)
        .options(
            joinedload(Team.course).joinedload(Course.nucleo),
            joinedload(Team.modality).joinedload(Modality.modality_type),
        )
        .filter(Team.team_id == team_id)
        .first()
    )

    if not team or team.deleted_at:
        # Delete projection if team no longer exists or is deleted
        session.query(TeamDetailView).filter(TeamDetailView.team_id == team_id).delete()
        return

    # Compute player count
    players_data = (
        session.query(TeamPlayer, Student)
        .join(Student, TeamPlayer.student_id == Student.student_id)
        .filter(
            TeamPlayer.team_id == team_id,
            TeamPlayer.removed_at.is_(None),
            Student.deleted_at.is_(None),
        )
        .all()
    )

    course = team.course
    nucleo = course.nucleo if course else None
    modality = team.modality
    modality_type = modality.modality_type if modality else None

    # Build projection row
    projection = TeamDetailView(
        team_id=team.team_id,
        team_name=team.name,
        team_season_id=team.season_id,
        course_id=course.course_id if course else None,
        course_name=course.name if course else "",
        course_abbreviation=course.abbreviation if course else "",
        nucleo_id=nucleo.nucleo_id if nucleo else None,
        nucleo_name=nucleo.name if nucleo else "",
        nucleo_abbreviation=nucleo.abbreviation if nucleo else "",
        modality_id=modality.modality_id if modality else None,
        modality_name=modality.name if modality else None,
        modality_type_id=modality_type.modality_type_id if modality_type else None,
        modality_type_name=modality_type.name if modality_type else "",
        player_count=len(players_data),
        players=[
            {
                "student_id": str(s.student_id),
                "student_number": s.student_number,
                "full_name": s.full_name,
                "is_member": s.is_member,
            }
            for _, s in players_data
        ],
    )

    # UPSERT (merge = deterministic projection rebuild)
    session.merge(projection)


# ==================== Student Detail View ====================


def rebuild_student_projection(session: Session, student_id: UUID) -> None:
    """
    Rebuild mv_student_details for a specific student.

    Dependencies: Student, Course, Nucleo, TeamPlayer

    Call when:
    - Student created/updated/deleted
    - Course updated
    - Nucleo updated
    - TeamPlayer added/removed
    """
    # Load canonical state with relationships
    student = (
        session.query(Student)
        .options(joinedload(Student.course).joinedload(Course.nucleo))
        .filter(Student.student_id == student_id)
        .first()
    )

    if not student or student.deleted_at:
        # Delete projection if student no longer exists or is deleted
        session.query(StudentDetailView).filter(
            StudentDetailView.student_id == student_id
        ).delete()
        return

    # Compute team count
    team_count = (
        session.query(func.count(TeamPlayer.id))
        .filter(
            TeamPlayer.student_id == student_id,
            TeamPlayer.removed_at.is_(None),
        )
        .scalar()
        or 0
    )

    course = student.course
    nucleo = course.nucleo if course else None

    # Build projection row
    projection = StudentDetailView(
        student_id=student.student_id,
        student_number=student.student_number,
        full_name=student.full_name,
        is_member=student.is_member,
        course_id=course.course_id if course else None,
        course_name=course.name if course else "",
        course_abbreviation=course.abbreviation if course else "",
        nucleo_id=nucleo.nucleo_id if nucleo else None,
        nucleo_name=nucleo.name if nucleo else "",
        nucleo_abbreviation=nucleo.abbreviation if nucleo else "",
        team_count=team_count,
    )

    # UPSERT (merge = deterministic projection rebuild)
    session.merge(projection)


# ==================== Tournament Detail View ====================


def rebuild_tournament_projection(session: Session, tournament_id: UUID) -> None:
    """
    Rebuild mv_tournament_details for a specific tournament.

    Dependencies: Tournament, Modality, ModalityType, TournamentCompetitor, Match

    Call when:
    - Tournament created/updated/deleted/finished
    - Modality updated
    - ModalityType updated
    - TournamentCompetitor added/removed
    - Match created/deleted
    """
    # Load canonical state with relationships
    tournament = (
        session.query(Tournament)
        .options(joinedload(Tournament.modality).joinedload(Modality.modality_type))
        .filter(Tournament.tournament_id == tournament_id)
        .first()
    )

    if not tournament or tournament.deleted_at:
        # Delete projection if tournament no longer exists or is deleted
        session.query(TournamentDetailView).filter(
            TournamentDetailView.tournament_id == tournament_id
        ).delete()
        return

    # Compute aggregated statistics
    competitor_count = (
        session.query(func.count(TournamentCompetitor.competitor_id))
        .filter(
            TournamentCompetitor.tournament_id == tournament_id,
            TournamentCompetitor.deleted_at.is_(None),
        )
        .scalar()
        or 0
    )

    match_count = (
        session.query(func.count(Match.match_id))
        .filter(
            Match.tournament_id == tournament_id,
            Match.deleted_at.is_(None),
        )
        .scalar()
        or 0
    )

    modality = tournament.modality
    modality_type = modality.modality_type if modality else None

    # Build projection row
    projection = TournamentDetailView(
        tournament_id=tournament.tournament_id,
        tournament_name=tournament.name,
        tournament_season_id=tournament.season_id,
        start_date=tournament.start_date,
        status=tournament.status,
        modality_id=modality.modality_id if modality else None,
        modality_name=modality.name if modality else None,
        modality_type_id=modality_type.modality_type_id if modality_type else None,
        modality_type_name=modality_type.name if modality_type else "",
        competitor_count=competitor_count,
        match_count=match_count,
    )

    # UPSERT (merge = deterministic projection rebuild)
    session.merge(projection)


# ==================== Match Detail View ====================


def rebuild_match_projection(session: Session, match_id: UUID) -> None:
    """
    Rebuild mv_match_details for a specific match.

    Dependencies: Match, Tournament, Modality, MatchParticipant, MatchResult, MatchComment

    Call when:
    - Match created/updated/deleted
    - MatchParticipant added/removed
    - MatchResult updated
    - MatchComment added/deleted
    """
    # Load canonical state with relationships
    match = (
        session.query(Match)
        .options(
            joinedload(Match.tournament).joinedload(Tournament.modality),
        )
        .filter(Match.match_id == match_id)
        .first()
    )

    if not match or match.deleted_at:
        # Delete projection if match no longer exists or is deleted
        session.query(MatchDetailView).filter(
            MatchDetailView.match_id == match_id
        ).delete()
        return

    # Get participants with their details
    # participant_id is now the competitor_id from TournamentCompetitor
    participants_data = (
        session.query(MatchParticipant, TournamentCompetitor)
        .join(
            TournamentCompetitor,
            MatchParticipant.participant_id == TournamentCompetitor.competitor_id,
        )
        .filter(
            MatchParticipant.match_id == match_id,
            MatchParticipant.removed_at.is_(None),
            TournamentCompetitor.deleted_at.is_(None),
        )
        .all()
    )

    participants = []
    for p, competitor in participants_data:
        # Get the entity name based on competitor type
        if competitor.competitor_type.value == "team":
            entity = (
                session.query(Team)
                .filter(Team.team_id == competitor.competitor_entity_id)
                .first()
            )
            participant_name = entity.name if entity else "Unknown Team"
        else:  # athlete/student
            entity = (
                session.query(Student)
                .filter(Student.student_id == competitor.competitor_entity_id)
                .first()
            )
            participant_name = entity.full_name if entity else "Unknown Athlete"

        participants.append(
            {
                "participant_id": str(p.participant_id),
                "competitor_id": str(competitor.competitor_id),
                "participant_type": competitor.competitor_type.value,
                "competitor_entity_id": str(competitor.competitor_entity_id),
                "participant_name": participant_name,
            }
        )

    # Get results
    results_data = (
        session.query(MatchResult)
        .join(
            MatchParticipant,
            MatchResult.participant_id == MatchParticipant.participant_id,
        )
        .filter(MatchResult.match_id == match_id)
        .all()
    )

    results = []
    for r in results_data:
        results.append(
            {
                "participant_id": str(r.participant_id),
                "score": r.score,
                "position": r.position,
                "results_metadata": r.results_metadata,
            }
        )

    # Compute comment count
    comment_count = (
        session.query(func.count(MatchComment.comment_id))
        .filter(
            MatchComment.match_id == match_id,
            MatchComment.deleted_at.is_(None),
        )
        .scalar()
        or 0
    )

    tournament = match.tournament
    modality = tournament.modality if tournament else None

    # Build projection row
    projection = MatchDetailView(
        match_id=match.match_id,
        location=match.location,
        status=match.status.value,
        start_time=match.start_time,
        tournament_id=tournament.tournament_id if tournament else None,
        tournament_name=tournament.name if tournament else "",
        modality_id=modality.modality_id if modality else None,
        modality_name=modality.name if modality else None,
        participants=participants,
        results=results if results else None,
        participant_count=len(participants),
        comment_count=comment_count,
    )

    # UPSERT (merge = deterministic projection rebuild)
    session.merge(projection)


# ==================== Tournament Standings View ====================


def rebuild_tournament_standings(session: Session, tournament_id: UUID) -> None:
    """
    Rebuild mv_tournament_standings for all competitors in a tournament.

    Dependencies: Tournament, TournamentCompetitor, Match, MatchParticipant, MatchResult

    Call when:
    - MatchResult updated
    - TournamentCompetitor added/removed
    - Match completed
    """
    # Always delete current standings before rebuild
    session.query(TournamentStandingsView).filter(
        TournamentStandingsView.tournament_id == tournament_id
    ).delete()

    # Get all active competitors in the tournament
    competitors = (
        session.query(TournamentCompetitor)
        .filter(
            TournamentCompetitor.tournament_id == tournament_id,
            TournamentCompetitor.deleted_at.is_(None),
        )
        .all()
    )

    if not competitors:
        return

    # Get all completed matches for this tournament
    matches = (
        session.query(Match.match_id)
        .filter(
            Match.tournament_id == tournament_id,
            Match.status.in_(["completed", "finished"]),
            Match.deleted_at.is_(None),
        )
        .all()
    )
    match_ids = [m[0] for m in matches]

    for competitor in competitors:
        competitor_entity_id = competitor.competitor_entity_id
        competitor_type = competitor.competitor_type.value

        # Get competitor name
        if competitor_type == "team":
            entity = (
                session.query(Team).filter(Team.team_id == competitor_entity_id).first()
            )
            competitor_name = entity.name if entity else "Unknown Team"
        else:  # athlete/student
            entity = (
                session.query(Student)
                .filter(Student.student_id == competitor_entity_id)
                .first()
            )
            competitor_name = entity.full_name if entity else "Unknown Athlete"

        # Calculate statistics
        # Pass competitor_id which is now the participant_id in match participants
        stats = _calculate_competitor_stats(
            session, competitor.competitor_id, match_ids
        )

        # Build projection row
        projection = TournamentStandingsView(
            tournament_id=tournament_id,
            competitor_type=competitor_type,
            competitor_entity_id=competitor_entity_id,
            competitor_name=competitor_name,
            matches_played=stats["matches_played"],
            wins=stats["wins"],
            losses=stats["losses"],
            draws=stats["draws"],
            points=stats["points"],
            total_score=stats["total_score"],
            rank=None,  # Will be calculated after all competitors are inserted
            statistics_metadata=stats.get("metadata"),
        )

        # UPSERT (merge = deterministic projection rebuild)
        session.merge(projection)

    # After all competitors are updated, calculate ranks
    _update_tournament_ranks(session, tournament_id)


def _calculate_competitor_stats(
    session: Session, competitor_id: UUID, match_ids: List[UUID]
) -> dict:
    """
    Calculate statistics for a competitor based on completed matches.

    competitor_id is the competitor_id from TournamentCompetitor which
    is also the participant_id in MatchParticipant.
    """
    if not match_ids:
        return {
            "matches_played": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "points": 0,
            "total_score": 0,
        }

    # Get all match participations
    # participant_id is now the competitor_id
    participations = (
        session.query(MatchParticipant, MatchResult)
        .join(
            MatchResult,
            MatchParticipant.participant_id == MatchResult.participant_id,
        )
        .filter(
            MatchParticipant.participant_id == competitor_id,
            MatchParticipant.match_id.in_(match_ids),
            MatchParticipant.removed_at.is_(None),
        )
        .all()
    )

    matches_played = len(participations)
    wins = 0
    losses = 0
    draws = 0
    total_score = 0

    for participant, result in participations:
        if result.score is not None:
            total_score += result.score

        # Determine win/loss/draw based on position
        # position == 1 is a win, position > 1 is a loss
        # This is a simple heuristic - adjust based on your sport rules
        if result.position == 1:
            wins += 1
        elif result.position is not None and result.position > 1:
            # Check if it's a draw (same score as position 1)
            # For now, treat position > 1 as loss
            losses += 1

    # Simple point system: 3 points for win, 1 for draw, 0 for loss
    points = (wins * 3) + (draws * 1)

    return {
        "matches_played": matches_played,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "points": points,
        "total_score": total_score,
    }


def _update_tournament_ranks(session: Session, tournament_id: UUID) -> None:
    """
    Update ranks for all competitors in a tournament based on points and total_score.
    """
    # Get all standings ordered by points (desc) and total_score (desc)
    standings = (
        session.query(TournamentStandingsView)
        .filter(TournamentStandingsView.tournament_id == tournament_id)
        .order_by(
            TournamentStandingsView.points.desc(),
            TournamentStandingsView.total_score.desc(),
        )
        .all()
    )

    # Assign ranks
    for rank, standing in enumerate(standings, start=1):
        standing.rank = rank


# ==================== Ranking Views ====================


def rebuild_general_ranking_projection(session: Session, season_id: int) -> None:
    """
    Rebuild the general rankings materialized view from core ranking data.

    This function clears the existing ``GeneralRankingView`` entries, reads all rows from the
    ``GeneralRankings`` core table, orders them by points in descending order, assigns ranks,
    and enriches each entry with course and nucleo information before persisting the projection.
    """
    from .models import GeneralRankings, GeneralRankingView

    # Clear existing general ranking view
    session.query(GeneralRankingView).filter(
        GeneralRankingView.season_id == season_id
    ).delete()

    general_rankings_core_data = (
        session.query(GeneralRankings)
        .filter(GeneralRankings.season_id == season_id)
        .all()
    )

    for rank, entry in enumerate(
        sorted(general_rankings_core_data, key=lambda x: x.points, reverse=True),
        start=1,
    ):
        course = (
            session.query(Course).filter(Course.course_id == entry.course_id).first()
        )
        nucleo = course.nucleo if course else None

        projection = GeneralRankingView(
            season_id=entry.season_id,
            course_id=course.course_id,
            course_name=course.name,
            course_abbreviation=course.abbreviation,
            nucleo_id=nucleo.nucleo_id,
            nucleo_name=nucleo.name,
            nucleo_abbreviation=nucleo.abbreviation,
            points=entry.points,
            rank=rank,
            tournaments_participated=entry.tournaments_participated,
        )
        session.merge(projection)


def rebuild_modality_ranking_projection(session: Session, season_id: int) -> None:
    """
    Rebuild modality rankings view.

    This is a placeholder function. The actual implementation would depend on the ranking logic,
    which may involve aggregating points from modalities, tournaments, or other entities.
    """
    from .models import ModalityRankings, ModalityRankingView

    # Clear existing modality ranking view
    session.query(ModalityRankingView).filter(
        ModalityRankingView.season_id == season_id
    ).delete()

    modality_rankings_core_data = (
        session.query(ModalityRankings)
        .filter(ModalityRankings.season_id == season_id)
        .all()
    )

    # grup by modality_id
    modality_groups: Dict[UUID, List[ModalityRankings]] = {}
    for entry in modality_rankings_core_data:
        modality_groups.setdefault(entry.modality_id, []).append(entry)

    for modality_id, entries in modality_groups.items():
        modality = (
            session.query(Modality).filter(Modality.modality_id == modality_id).first()
        )
        modality_name = modality.name if modality else "Unknown Modality"

        for rank, entry in enumerate(
            sorted(entries, key=lambda x: x.points, reverse=True),
            start=1,
        ):
            course = (
                session.query(Course)
                .filter(Course.course_id == entry.course_id)
                .first()
            )
            nucleo = course.nucleo if course else None

            projection = ModalityRankingView(
                season_id=entry.season_id,
                modality_id=modality_id,
                modality_name=modality_name,
                course_id=course.course_id,
                course_name=course.name,
                course_abbreviation=course.abbreviation,
                nucleo_id=nucleo.nucleo_id,
                nucleo_name=nucleo.name,
                nucleo_abbreviation=nucleo.abbreviation,
                points=entry.points,
                rank=rank,
            )
            session.merge(projection)


# ==================== Nucleo Views ====================


def rebuild_nucleo_projection(session: Session, nucleo_id: UUID) -> None:
    """Rebuild the projection for a specific nucleo.

    Dependencies: Nucleo

    Call when:
        - Nucleo created/updated/deleted
    """
    from .models import Nucleo, NucleoDetailView

    nucleo = session.query(Nucleo).filter(Nucleo.nucleo_id == nucleo_id).first()

    if not nucleo or nucleo.deleted_at:
        # Delete projection if nucleo no longer exists or is deleted
        session.query(NucleoDetailView).filter(
            NucleoDetailView.nucleo_id == nucleo_id
        ).delete()
        return

    projection = NucleoDetailView(
        nucleo_id=nucleo.nucleo_id,
        name=nucleo.name,
        abbreviation=nucleo.abbreviation,
        logo_url=nucleo.logo_url,
    )

    session.merge(projection)


# ==================== Season Views ====================


def rebuild_season_projection(session: Session, season_id: int) -> None:
    """Rebuild the projection for a specific season.

    Dependencies: Season

    Call when:
        - Season created/updated/deleted
    """
    from .models import Season, SeasonDetailView

    season = session.query(Season).filter(Season.season_id == season_id).first()

    if not season:
        # Delete projection if season no longer exists
        session.query(SeasonDetailView).filter(
            SeasonDetailView.season_id == season_id
        ).delete()
        return

    projection = SeasonDetailView(
        season_id=season.season_id,
        name=season.name,
    )

    session.merge(projection)


# ==================== Bulk Rebuild Utilities ====================


def rebuild_all_teams_for_course(session: Session, course_id: UUID) -> None:
    """Rebuild all team projections for teams in a specific course."""
    teams = session.query(Team.team_id).filter(Team.course_id == course_id).all()
    for (team_id,) in teams:
        rebuild_team_projection(session, team_id)


def rebuild_all_students_for_course(session: Session, course_id: UUID) -> None:
    """Rebuild all student projections for students in a specific course."""
    students = (
        session.query(Student.student_id).filter(Student.course_id == course_id).all()
    )
    for (student_id,) in students:
        rebuild_student_projection(session, student_id)


def rebuild_all_teams_for_modality(session: Session, modality_id: UUID) -> None:
    """Rebuild all team projections for teams in a specific modality."""
    teams = session.query(Team.team_id).filter(Team.modality_id == modality_id).all()
    for (team_id,) in teams:
        rebuild_team_projection(session, team_id)


def rebuild_all_tournaments_for_modality(session: Session, modality_id: UUID) -> None:
    """Rebuild all tournament projections for tournaments in a specific modality."""
    tournaments = (
        session.query(Tournament.tournament_id)
        .filter(Tournament.modality_id == modality_id)
        .all()
    )
    for (tournament_id,) in tournaments:
        rebuild_tournament_projection(session, tournament_id)


def rebuild_all_matches_for_tournament(session: Session, tournament_id: UUID) -> None:
    """Rebuild all match projections for matches in a specific tournament."""
    matches = (
        session.query(Match.match_id).filter(Match.tournament_id == tournament_id).all()
    )
    for (match_id,) in matches:
        rebuild_match_projection(session, match_id)


def rebuild_all_nucleos(session: Session) -> None:
    """Rebuild projections for all nucleos."""
    nucleos = session.query(Nucleo.nucleo_id).all()
    for (nucleo_id,) in nucleos:
        rebuild_nucleo_projection(session, nucleo_id)


def rebuild_all_seasons(session: Session) -> None:
    """Rebuild projections for all seasons."""
    seasons = session.query(Season.season_id).all()
    for (season_id,) in seasons:
        rebuild_season_projection(session, season_id)
