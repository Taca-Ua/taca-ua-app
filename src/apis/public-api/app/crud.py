"""
CRUD operations for Public API.

This module provides read-only operations on the materialized views
in the public_read schema.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session
from taca_models import (
    MatchDetailView,
    StudentDetailView,
    TeamDetailView,
    TournamentDetailView,
    TournamentStandingsView,
)

# ==================== Team Detail View Operations ====================


def get_teams(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    course_id: Optional[UUID] = None,
    nucleo_id: Optional[UUID] = None,
    modality_id: Optional[UUID] = None,
) -> tuple[list[TeamDetailView], int]:
    """
    Get list of teams with pagination and optional filters.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        course_id: Filter by course ID
        nucleo_id: Filter by nucleo ID
        modality_id: Filter by modality ID

    Returns:
        Tuple of (list of teams, total count)
    """
    query = db.query(TeamDetailView)

    # Apply filters
    if course_id:
        query = query.filter(TeamDetailView.course_id == course_id)
    if nucleo_id:
        query = query.filter(TeamDetailView.nucleo_id == nucleo_id)
    if modality_id:
        query = query.filter(TeamDetailView.modality_id == modality_id)

    # Get total count
    total = query.count()

    # Apply pagination
    teams = query.offset(skip).limit(limit).all()

    return teams, total


def get_team_by_id(db: Session, team_id: UUID) -> Optional[TeamDetailView]:
    """
    Get a specific team by ID.

    Args:
        db: Database session
        team_id: Team identifier

    Returns:
        Team detail or None if not found
    """
    return db.query(TeamDetailView).filter(TeamDetailView.team_id == team_id).first()


# ==================== Student Detail View Operations ====================


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    course_id: Optional[UUID] = None,
    nucleo_id: Optional[UUID] = None,
    is_member: Optional[bool] = None,
    search: Optional[str] = None,
) -> tuple[list[StudentDetailView], int]:
    """
    Get list of students with pagination and optional filters.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        course_id: Filter by course ID
        nucleo_id: Filter by nucleo ID
        is_member: Filter by membership status
        search: Search in student name or number

    Returns:
        Tuple of (list of students, total count)
    """
    query = db.query(StudentDetailView)

    # Apply filters
    if course_id:
        query = query.filter(StudentDetailView.course_id == course_id)
    if nucleo_id:
        query = query.filter(StudentDetailView.nucleo_id == nucleo_id)
    if is_member is not None:
        query = query.filter(StudentDetailView.is_member == is_member)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                StudentDetailView.full_name.ilike(search_pattern),
                StudentDetailView.student_number.ilike(search_pattern),
            )
        )

    # Get total count
    total = query.count()

    # Apply pagination
    students = query.offset(skip).limit(limit).all()

    return students, total


def get_student_by_id(db: Session, student_id: UUID) -> Optional[StudentDetailView]:
    """
    Get a specific student by ID.

    Args:
        db: Database session
        student_id: Student identifier

    Returns:
        Student detail or None if not found
    """
    return (
        db.query(StudentDetailView)
        .filter(StudentDetailView.student_id == student_id)
        .first()
    )


def get_student_by_number(
    db: Session, student_number: str
) -> Optional[StudentDetailView]:
    """
    Get a specific student by student number.

    Args:
        db: Database session
        student_number: Student number

    Returns:
        Student detail or None if not found
    """
    return (
        db.query(StudentDetailView)
        .filter(StudentDetailView.student_number == student_number)
        .first()
    )


# ==================== Tournament Detail View Operations ====================


def get_tournaments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    modality_id: Optional[UUID] = None,
    status: Optional[str] = None,
) -> tuple[list[TournamentDetailView], int]:
    """
    Get list of tournaments with pagination and optional filters.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        modality_id: Filter by modality ID
        status: Filter by tournament status

    Returns:
        Tuple of (list of tournaments, total count)
    """
    query = db.query(TournamentDetailView)

    # Apply filters
    if modality_id:
        query = query.filter(TournamentDetailView.modality_id == modality_id)
    if status:
        query = query.filter(TournamentDetailView.status == status)

    # Get total count
    total = query.count()

    # Apply pagination and order by start date descending
    tournaments = (
        query.order_by(TournamentDetailView.start_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return tournaments, total


def get_tournament_by_id(
    db: Session, tournament_id: UUID
) -> Optional[TournamentDetailView]:
    """
    Get a specific tournament by ID.

    Args:
        db: Database session
        tournament_id: Tournament identifier

    Returns:
        Tournament detail or None if not found
    """
    return (
        db.query(TournamentDetailView)
        .filter(TournamentDetailView.tournament_id == tournament_id)
        .first()
    )


# ==================== Match Detail View Operations ====================


def get_matches(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    tournament_id: Optional[UUID] = None,
    status: Optional[str] = None,
) -> tuple[list[MatchDetailView], int]:
    """
    Get list of matches with pagination and optional filters.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        tournament_id: Filter by tournament ID
        status: Filter by match status

    Returns:
        Tuple of (list of matches, total count)
    """
    query = db.query(MatchDetailView)

    # Apply filters
    if tournament_id:
        query = query.filter(MatchDetailView.tournament_id == tournament_id)
    if status:
        query = query.filter(MatchDetailView.status == status)

    # Get total count
    total = query.count()

    # Apply pagination and order by start time descending
    matches = (
        query.order_by(MatchDetailView.start_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return matches, total


def get_match_by_id(db: Session, match_id: UUID) -> Optional[MatchDetailView]:
    """
    Get a specific match by ID.

    Args:
        db: Database session
        match_id: Match identifier

    Returns:
        Match detail or None if not found
    """
    return (
        db.query(MatchDetailView).filter(MatchDetailView.match_id == match_id).first()
    )


# ==================== Tournament Standings View Operations ====================


def get_tournament_standings(
    db: Session,
    tournament_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[TournamentStandingsView], int]:
    """
    Get tournament standings with pagination.

    Args:
        db: Database session
        tournament_id: Tournament identifier
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of standings, total count)
    """
    query = db.query(TournamentStandingsView).filter(
        TournamentStandingsView.tournament_id == tournament_id
    )

    # Get total count
    total = query.count()

    # Apply pagination and order by rank
    standings = (
        query.order_by(TournamentStandingsView.rank.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return standings, total


def get_standings_by_competitor(
    db: Session, competitor_entity_id: UUID
) -> list[TournamentStandingsView]:
    """
    Get all standings for a specific competitor across tournaments.

    Args:
        db: Database session
        competitor_entity_id: Competitor entity ID (team_id or student_id)

    Returns:
        List of standings for the competitor
    """
    return (
        db.query(TournamentStandingsView)
        .filter(TournamentStandingsView.competitor_entity_id == competitor_entity_id)
        .all()
    )
