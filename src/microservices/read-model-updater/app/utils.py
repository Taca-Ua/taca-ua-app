"""
Projection rebuild utilities for materialized views.

These functions query core tables and update materialized views.
They should be called after core table updates (from events or snapshot rebuilds).
"""

from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .models import (
    Course,
    GeneralRankingView,
    Match,
    MatchComment,
    MatchDetailView,
    MatchParticipant,
    MatchResult,
    Modality,
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
    player_count = (
        session.query(func.count(TeamPlayer.id))
        .filter(
            TeamPlayer.team_id == team_id,
            TeamPlayer.removed_at.is_(None),
        )
        .scalar()
        or 0
    )

    course = team.course
    nucleo = course.nucleo if course else None
    modality = team.modality
    modality_type = modality.modality_type if modality else None

    # Build projection row
    projection = TeamDetailView(
        team_id=team.team_id,
        team_name=team.name,
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
        player_count=player_count,
        updated_at=datetime.utcnow(),
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
        updated_at=datetime.utcnow(),
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
        start_date=tournament.start_date,
        status=tournament.status,
        modality_id=modality.modality_id if modality else None,
        modality_name=modality.name if modality else None,
        modality_type_id=modality_type.modality_type_id if modality_type else None,
        modality_type_name=modality_type.name if modality_type else "",
        competitor_count=competitor_count,
        match_count=match_count,
        updated_at=datetime.utcnow(),
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
    participants_data = (
        session.query(MatchParticipant)
        .filter(
            MatchParticipant.match_id == match_id,
            MatchParticipant.removed_at.is_(None),
        )
        .all()
    )

    participants = []
    for p in participants_data:
        if p.participant_type == "team":
            entity = (
                session.query(Team)
                .filter(Team.team_id == p.participant_entity_id)
                .first()
            )
            participant_name = entity.name if entity else "Unknown Team"
        else:  # athlete/student
            entity = (
                session.query(Student)
                .filter(Student.student_id == p.participant_entity_id)
                .first()
            )
            participant_name = entity.full_name if entity else "Unknown Athlete"

        participants.append(
            {
                "participant_id": str(p.participant_id),
                "participant_type": p.participant_type.value,
                "participant_entity_id": str(p.participant_entity_id),
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
        updated_at=datetime.utcnow(),
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
        stats = _calculate_competitor_stats(session, competitor_entity_id, match_ids)

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
            updated_at=datetime.utcnow(),
        )

        # UPSERT (merge = deterministic projection rebuild)
        session.merge(projection)

    # After all competitors are updated, calculate ranks
    _update_tournament_ranks(session, tournament_id)


def _calculate_competitor_stats(
    session: Session, competitor_entity_id: UUID, match_ids: List[UUID]
) -> dict:
    """
    Calculate statistics for a competitor based on completed matches.
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
    participations = (
        session.query(MatchParticipant, MatchResult)
        .join(
            MatchResult,
            MatchParticipant.participant_id == MatchResult.participant_id,
        )
        .filter(
            MatchParticipant.participant_entity_id == competitor_entity_id,
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
        standing.updated_at = datetime.utcnow()


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


# ==================== General Ranking View ====================


def rebuild_general_ranking(session: Session) -> None:
    """
    Rebuild mv_general_ranking for all courses.

    This calculates points earned by each course based on tournament final rankings.
    Points are determined by the modality_type's escaloes configuration, which
    defines point awards based on position and participant count.

    Call when:
    - TournamentRanking entries are created/updated
    - During full projection rebuild

    Algorithm:
    1. For each finished tournament with rankings:
       - Determine the escalao based on participant count
       - For each ranking entry, calculate points based on position
       - Aggregate points to the team's course
    2. Rank courses by total points
    """
    # Clear existing general ranking data
    session.query(GeneralRankingView).delete()

    # Dictionary to accumulate points per course
    # course_id -> {points, tournament_count, course_name, course_abbr, nucleo_id, nucleo_name, nucleo_abbr}
    course_points = {}

    # Get distinct tournament IDs that are finished and have rankings
    # We do this in two steps to avoid DISTINCT with JSON columns
    tournament_ids = (
        session.query(Tournament.tournament_id)
        .join(
            TournamentRanking,
            Tournament.tournament_id == TournamentRanking.tournament_id,
        )
        .filter(Tournament.status == "finished")
        .distinct()
        .all()
    )

    # Now load each tournament with its relationships
    tournaments_with_rankings = []
    for (tournament_id,) in tournament_ids:
        tournament = (
            session.query(Tournament)
            .filter(Tournament.tournament_id == tournament_id)
            .options(
                joinedload(Tournament.modality).joinedload(Modality.modality_type),
            )
            .first()
        )
        if tournament:
            tournaments_with_rankings.append(tournament)

    for tournament in tournaments_with_rankings:
        modality_type = tournament.modality.modality_type
        escaloes = modality_type.escaloes

        # Determine participant count for this tournament
        # If competitors are teams, count total athletes across all teams
        # If competitors are athletes, count total athletes
        competitor_type_result = (
            session.query(TournamentCompetitor.competitor_type)
            .filter(
                TournamentCompetitor.tournament_id == tournament.tournament_id,
                TournamentCompetitor.deleted_at.is_(None),
            )
            .first()
        )

        if not competitor_type_result:
            continue  # No competitors, skip this tournament

        competitor_type = competitor_type_result[0]

        if competitor_type == "team":
            # Count total active athletes across all teams in tournament
            participant_count = (
                session.query(func.count(TeamPlayer.id))
                .join(
                    TournamentCompetitor,
                    TournamentCompetitor.competitor_entity_id == TeamPlayer.team_id,
                )
                .filter(
                    TournamentCompetitor.tournament_id == tournament.tournament_id,
                    TournamentCompetitor.deleted_at.is_(None),
                    TournamentCompetitor.competitor_type == "team",
                    TeamPlayer.removed_at.is_(None),
                )
                .scalar()
                or 0
            )
        else:  # athlete
            # Count number of athlete competitors
            participant_count = (
                session.query(func.count(TournamentCompetitor.competitor_id))
                .filter(
                    TournamentCompetitor.tournament_id == tournament.tournament_id,
                    TournamentCompetitor.deleted_at.is_(None),
                    TournamentCompetitor.competitor_type == "athlete",
                )
                .scalar()
                or 0
            )

        # Find the appropriate escalao based on participant count
        selected_escalao = None
        for escalao in escaloes:
            min_part = escalao.get("minParticipants")
            max_part = escalao.get("maxParticipants")

            # Check if participant count falls within this escalao's range
            if min_part is None and max_part is None:
                selected_escalao = escalao
                break
            elif min_part is None and participant_count <= max_part:
                selected_escalao = escalao
                break
            elif max_part is None and participant_count >= min_part:
                selected_escalao = escalao
                break
            elif min_part <= participant_count <= max_part:
                selected_escalao = escalao
                break

        if not selected_escalao:
            continue  # No matching escalao, skip this tournament

        points_array = selected_escalao.get("points", [])

        # Get all ranking entries for this tournament
        rankings = (
            session.query(TournamentRanking)
            .join(Team, TournamentRanking.team_id == Team.team_id)
            .join(Course, Team.course_id == Course.course_id)
            .options(
                joinedload(TournamentRanking.tournament),
            )
            .filter(TournamentRanking.tournament_id == tournament.tournament_id)
            .all()
        )

        # Track which courses participated in this tournament
        tournament_courses = set()

        for ranking in rankings:
            # Get team and course info
            team = session.query(Team).filter(Team.team_id == ranking.team_id).first()
            if not team:
                continue

            course = (
                session.query(Course)
                .options(joinedload(Course.nucleo))
                .filter(Course.course_id == team.course_id)
                .first()
            )
            if not course:
                continue

            tournament_courses.add(course.course_id)

            # Calculate points for this position
            position_index = ranking.position - 1  # Convert to 0-based index
            if 0 <= position_index < len(points_array):
                points = points_array[position_index]
            else:
                points = 0  # No points if position is beyond defined points

            # Initialize course entry if not exists
            if course.course_id not in course_points:
                nucleo = course.nucleo
                course_points[course.course_id] = {
                    "course_id": course.course_id,
                    "course_name": course.name,
                    "course_abbreviation": course.abbreviation,
                    "nucleo_id": nucleo.nucleo_id if nucleo else None,
                    "nucleo_name": nucleo.name if nucleo else "",
                    "nucleo_abbreviation": nucleo.abbreviation if nucleo else "",
                    "points": 0,
                    "tournaments_participated": 0,
                }

            # Add points to course
            course_points[course.course_id]["points"] += points

        # Increment tournament count for participating courses
        for course_id in tournament_courses:
            if course_id in course_points:
                course_points[course_id]["tournaments_participated"] += 1

    # Sort courses by points (descending) and assign ranks
    sorted_courses = sorted(
        course_points.values(), key=lambda x: x["points"], reverse=True
    )

    rank = 1
    for idx, course_data in enumerate(sorted_courses):
        # Assign rank (handle ties)
        if idx > 0 and course_data["points"] == sorted_courses[idx - 1]["points"]:
            # Same points as previous, keep same rank
            course_data["rank"] = sorted_courses[idx - 1]["rank"]
        else:
            course_data["rank"] = rank

        # Create GeneralRankingView entry
        ranking_view = GeneralRankingView(
            course_id=course_data["course_id"],
            course_name=course_data["course_name"],
            course_abbreviation=course_data["course_abbreviation"],
            nucleo_id=course_data["nucleo_id"],
            nucleo_name=course_data["nucleo_name"],
            nucleo_abbreviation=course_data["nucleo_abbreviation"],
            points=course_data["points"],
            rank=course_data["rank"],
            tournaments_participated=course_data["tournaments_participated"],
            updated_at=datetime.utcnow(),
        )
        session.add(ranking_view)

        rank += 1

    session.flush()
