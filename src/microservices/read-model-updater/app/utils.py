from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .models import (
    Course,
    Match,
    Modality,
    Team,
    TeamDetailView,
    Tournament,
    TournamentCompetitor,
    TournamentDetailView,
)


def rebuild_tournament_projection(session: Session, tournament_id):
    """
    Rebuild mv_tournament_details for a specific tournament.
    Must be called after canonical tables are updated.
    """

    # load canonical state with relationships
    tournament = (
        session.query(Tournament)
        .options(joinedload(Tournament.modality).joinedload(Modality.modality_type))
        .filter(Tournament.tournament_id == tournament_id)
        .first()
    )

    if not tournament or tournament.deleted_at:
        # Soft-delete projection if tournament no longer exists
        session.query(TournamentDetailView).filter(
            TournamentDetailView.tournament_id == tournament_id
        ).delete()
        return

    # compute aggregated statistics
    competitor_count = (
        session.query(func.count(TournamentCompetitor.competitor_id))
        .filter(
            TournamentCompetitor.tournament_id == tournament_id,
            TournamentCompetitor.deleted_at.is_(None),
        )
        .scalar()
    )

    match_count = (
        session.query(func.count(Match.match_id))
        .filter(
            Match.tournament_id == tournament_id,
            Match.deleted_at.is_(None),
        )
        .scalar()
    )

    modality = tournament.modality
    modality_type = modality.modality_type

    # build projection row
    projection = TournamentDetailView(
        tournament_id=tournament.tournament_id,
        tournament_name=tournament.name,
        start_date=tournament.start_date,
        status=tournament.status,
        modality_id=modality.modality_id,
        modality_name=modality.name,
        modality_type_id=modality_type.modality_type_id,
        modality_type_name=modality_type.name,
        competitor_count=competitor_count or 0,
        match_count=match_count or 0,
    )

    # UPSERT (merge = deterministic projection rebuild)
    session.merge(projection)


def rebuild_team_projection(session: Session, team_id):
    """
    Rebuild mv_team_details for a specific team.
    Must be called after canonical tables are updated.
    """
    # load canonical state with relationships
    team = (
        session.query(Team)
        .options(joinedload(Team.course).joinedload(Course.department))
        .filter(Team.team_id == team_id)
        .first()
    )

    if not team or team.deleted_at:
        # Soft-delete projection if team no longer exists
        session.query(TeamDetailView).filter(TeamDetailView.team_id == team_id).delete()
        return

    # compute aggregated statistics
    student_count = len(team.students)

    # build projection row
    projection = TeamDetailView(
        team_id=team.team_id,
        team_name=team.name,
        student_count=student_count or 0,
        course_id=team.course.course_id if team.course else None,
        department_id=(
            team.course.department.department_id
            if team.course and team.course.department
            else None
        ),
    )

    # UPSERT (merge = deterministic projection rebuild)
    session.merge(projection)


def rebuild_student_projection(session: Session, student_id):
    """
    Placeholder for student projection rebuild logic.
    Similar to tournament projection but focused on student details and stats.
    """
    pass


def rebuild_match_projection(session: Session, match_id):
    """
    Placeholder for match projection rebuild logic.
    Similar to tournament projection but focused on match details and stats.
    """
    pass


def rebuild_ranking_projection(session: Session, modality_id):
    """
    Placeholder for ranking projection rebuild logic.
    Similar to tournament projection but focused on ranking details and stats.
    """
    pass
