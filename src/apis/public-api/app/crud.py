"""
CRUD operations for Public API.

This module provides read-only operations on the materialized views
in the public_read schema. All read operations include caching via Redis.
"""

import datetime
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from .cache import CACHE_TTL, CacheKeyGenerator, cached
from .models import (
    CourseDetailView,
    GeneralRankingView,
    HomePageConfigView,
    MatchDetailView,
    ModalityRankingView,
    NucleoDetailView,
    RegulationDetailView,
    SeasonDetailView,
    StudentDetailView,
    TeamDetailView,
    TournamentDetailView,
    TournamentStandingsView,
)

# ==================== Nucleo Operations ====================


@cached(
    cache_key="",
    ttl=CACHE_TTL["nucleo_list"],
    key_builder=lambda db, skip=0, limit=100: CacheKeyGenerator.nucleo_list(
        skip, limit
    ),
)
def get_nucleos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[NucleoDetailView], int]:
    """
    Get list of nucleos (active only) with pagination.

    Returns:
        Tuple of (list of nucleos, total count)
    """
    query = db.query(NucleoDetailView).order_by(NucleoDetailView.name)
    total = query.count()
    return query.offset(skip).limit(limit).all(), total


@cached(
    cache_key="",
    ttl=CACHE_TTL["nucleo"],
    key_builder=lambda db, nucleo_id: CacheKeyGenerator.nucleo(nucleo_id),
)
def get_nucleo_by_id(db: Session, nucleo_id: UUID) -> Optional[NucleoDetailView]:
    """
    Get a specific nucleo by ID.

    Returns:
        Nucleo or None if not found
    """
    return (
        db.query(NucleoDetailView)
        .filter(NucleoDetailView.nucleo_id == nucleo_id)
        .first()
    )


# ==================== Team Detail View Operations ====================


@cached(
    cache_key="",
    ttl=CACHE_TTL["team_list"],
    key_builder=lambda db, skip=0, limit=100, course_id=None, nucleo_id=None, modality_id=None, season_id=None: CacheKeyGenerator.team_list(
        skip, limit, course_id, nucleo_id, modality_id, season_id
    ),
)
def get_teams(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    course_id: Optional[UUID] = None,
    nucleo_id: Optional[UUID] = None,
    modality_id: Optional[UUID] = None,
    season_id: Optional[int] = None,
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
        season_id: Filter by season ID
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
    if season_id:
        query = query.filter(TeamDetailView.team_season_id == season_id)

    # Get total count
    total = query.count()

    # Apply pagination
    teams = query.offset(skip).limit(limit).all()

    return teams, total


@cached(
    cache_key="",
    ttl=CACHE_TTL["team"],
    key_builder=lambda db, team_id: CacheKeyGenerator.team(team_id),
)
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


@cached(
    cache_key="",
    ttl=CACHE_TTL["student_list"],
    key_builder=lambda db, skip=0, limit=100, course_id=None, nucleo_id=None, is_member=None, search=None: CacheKeyGenerator.student_list(
        skip, limit, course_id, nucleo_id, is_member, search
    ),
)
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


@cached(
    cache_key="",
    ttl=CACHE_TTL["student"],
    key_builder=lambda db, student_id: CacheKeyGenerator.student(student_id),
)
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


@cached(
    cache_key="",
    ttl=CACHE_TTL["student"],
    key_builder=lambda db, student_number: CacheKeyGenerator.student_by_number(
        student_number
    ),
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


@cached(
    cache_key="",
    ttl=CACHE_TTL["tournament_list"],
    key_builder=lambda db, skip=0, limit=100, modality_id=None, status=None, season_id=None: CacheKeyGenerator.tournament_list(
        skip, limit, modality_id, status, season_id
    ),
)
def get_tournaments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    modality_id: Optional[UUID] = None,
    status: Optional[str] = None,
    season_id: Optional[int] = None,
) -> tuple[list[TournamentDetailView], int]:
    """
    Get list of tournaments with pagination and optional filters.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        modality_id: Filter by modality ID
        status: Filter by tournament status
        season_id: Filter by season ID
    Returns:
        Tuple of (list of tournaments, total count)
    """
    query = db.query(TournamentDetailView)

    # Apply filters
    if modality_id:
        query = query.filter(TournamentDetailView.modality_id == modality_id)
    if status:
        query = query.filter(TournamentDetailView.status == status)
    else:
        # Never expose draft tournaments on the public API
        query = query.filter(TournamentDetailView.status != "draft")
    if season_id:
        query = query.filter(TournamentDetailView.tournament_season_id == season_id)

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


@cached(
    cache_key="",
    ttl=CACHE_TTL["tournament"],
    key_builder=lambda db, tournament_id: CacheKeyGenerator.tournament(tournament_id),
)
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


@cached(
    cache_key="",
    ttl=CACHE_TTL["match_list"],
    key_builder=lambda db, skip=0, limit=100, tournament_id=None, status=None, date=None: CacheKeyGenerator.match_list(
        skip, limit, tournament_id, status, date
    ),
)
def get_matches(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    tournament_id: Optional[UUID] = None,
    status: Optional[str] = None,
    date: Optional[str] = None,
) -> tuple[list[MatchDetailView], int]:
    """
    Get list of matches with pagination and optional filters.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        tournament_id: Filter by tournament ID
        status: Filter by match status
        date: Filter by scheduled date (YYYY-MM)
    Returns:
        Tuple of (list of matches, total count)
    """
    query = db.query(MatchDetailView).filter(
        MatchDetailView.status != "draft",
        MatchDetailView.start_time != None,  # noqa: E711
    )

    # Apply filters
    if tournament_id:
        query = query.filter(MatchDetailView.tournament_id == tournament_id)
    if status:
        query = query.filter(MatchDetailView.status == status)
    if date:
        try:
            date_obj = datetime.datetime.strptime(date, "%Y-%m")
            query = query.filter(
                MatchDetailView.start_time >= date_obj,
                MatchDetailView.start_time < (date_obj + datetime.timedelta(days=31)),
            )
        except ValueError:
            # Invalid date format, ignore the filter
            pass

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


@cached(
    cache_key="",
    ttl=CACHE_TTL["match"],
    key_builder=lambda db, match_id: CacheKeyGenerator.match(match_id),
)
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


@cached(
    cache_key="",
    ttl=CACHE_TTL["ranking"],
    key_builder=lambda db, tournament_id, skip=0, limit=100: f"standings:{tournament_id}:{skip}:{limit}",
)
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
        query.order_by(TournamentStandingsView.position.asc().nullslast())
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


# ==================== General Ranking View Operations ====================


@cached(
    cache_key="",
    ttl=CACHE_TTL["ranking"],
    key_builder=lambda db, season_id, nucleo_id=None: f"ranking:general:{season_id}:{nucleo_id}",
)
def get_general_ranking(
    db: Session,
    season_id: int,
    nucleo_id: Optional[UUID] = None,
) -> tuple[list[GeneralRankingView], int]:
    """
    Get general ranking of all courses, ordered by points and rank.

    Args:
        db: Database session
        season_id: Season ID to filter the ranking
        nucleo_id: Optional filter by nucleo ID

    Returns:
        Tuple of (list of rankings, total count)
    """
    query = db.query(GeneralRankingView).filter(
        GeneralRankingView.season_id == season_id
    )

    # Apply filters
    if nucleo_id:
        query = query.filter(GeneralRankingView.nucleo_id == nucleo_id)

    # Order by rank (nulls last) and points descending
    query = query.order_by(
        GeneralRankingView.rank.asc().nullslast(),
        GeneralRankingView.points.desc(),
    )

    # Get total count
    total = query.count()

    # Get all rankings
    rankings = query.all()

    return rankings, total


@cached(
    cache_key="",
    ttl=CACHE_TTL["ranking"],
    key_builder=lambda db, course_id: f"ranking:course:{course_id}",
)
def get_course_ranking(db: Session, course_id: UUID) -> Optional[GeneralRankingView]:
    """
    Get ranking information for a specific course.

    Args:
        db: Database session
        course_id: Course identifier

    Returns:
        Ranking information or None if not found
    """
    return (
        db.query(GeneralRankingView)
        .filter(GeneralRankingView.course_id == course_id)
        .first()
    )


# ==================== Regulation Operations ====================


@cached(
    cache_key="",
    ttl=CACHE_TTL["regulation"],
    key_builder=lambda db, search=None, season_id=None: f"regulation:list:{search}:{season_id}",
)
def get_regulations(
    db: Session,
    search: Optional[str] = None,
    season_id: Optional[int] = None,
) -> list[RegulationDetailView]:
    """
    Get all regulations, optionally filtered by a search term.

    Args:
        db: Database session
        search: Optional search string matched against title and description
        season_id: Optional filter by season ID
    Returns:
        List of regulations ordered by creation date (newest first)
    """
    query = db.query(RegulationDetailView)

    if season_id:
        query = query.filter(RegulationDetailView.season_id == season_id)

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                RegulationDetailView.title.ilike(term),
                RegulationDetailView.description.ilike(term),
            )
        )

    return query.all()


# ==================== Modality Ranking View Operations ====================


@cached(
    cache_key="",
    ttl=CACHE_TTL["ranking"],
    key_builder=lambda db, season_id, modality_id=None, nucleo_id=None: f"ranking:modality:{season_id}:{modality_id}:{nucleo_id}",
)
def get_modality_ranking(
    db: Session,
    season_id: int,
    modality_id: Optional[UUID] = None,
    nucleo_id: Optional[UUID] = None,
) -> tuple[list[ModalityRankingView], int]:
    """Get rankings of courses within modalities.

    Results are ordered by rank (nulls last) and points descending.

    Args:
        db: Database session
        season_id: Season ID to filter the ranking
        modality_id: Optional filter by modality ID
        nucleo_id: Optional filter by nucleo ID

    Returns:
        Tuple of (list of rankings, total count)
    """
    query = db.query(ModalityRankingView).filter(
        ModalityRankingView.season_id == season_id
    )

    # Apply filters
    if modality_id:
        query = query.filter(ModalityRankingView.modality_id == modality_id)
    if nucleo_id:
        query = query.filter(ModalityRankingView.nucleo_id == nucleo_id)

    # Order by modality, then rank (nulls last) and points
    query = query.order_by(
        ModalityRankingView.modality_id,
        ModalityRankingView.rank.asc().nullslast(),
        ModalityRankingView.points.desc(),
    )

    # Get total count
    total = query.count()

    # Get all rankings
    rankings = query.all()

    return rankings, total


@cached(
    cache_key="",
    ttl=CACHE_TTL["ranking"],
    key_builder=lambda db, course_id: f"ranking:modality:course:{course_id}",
)
def get_course_modality_rankings(
    db: Session,
    course_id: UUID,
) -> list[ModalityRankingView]:
    """Get modality-specific rankings for a given course.

    Args:
        db: Database session
        course_id: Course identifier

    Returns:
        List of rankings for the course across modalities (may be empty)
    """
    return (
        db.query(ModalityRankingView)
        .filter(ModalityRankingView.course_id == course_id)
        .order_by(
            ModalityRankingView.modality_name.asc().nullslast(),
            ModalityRankingView.rank.asc().nullslast(),
        )
        .all()
    )


# ==================== Season View Operations ====================


@cached(
    cache_key="",
    ttl=CACHE_TTL["season"],
    key_builder=lambda db: "season:list",
)
def get_seasons(db: Session) -> Tuple[list[SeasonDetailView], int]:
    """Get list of all seasons.

    Returns:
        List of season details ordered by most recent first
    """

    query = db.query(SeasonDetailView).order_by(SeasonDetailView.season_id.desc())
    total = query.count()

    return query.all(), total


# ==================== Home Page Config View Operations ====================


@cached(
    cache_key="",
    ttl=CACHE_TTL["home_page_config"],
    key_builder=lambda db: "home_page_config",
)
def get_home_page_config(db: Session) -> Optional[dict]:
    """Get the home page configuration.

    Returns:
        Home page configuration as a dictionary or None if not set
    """
    config = db.query(HomePageConfigView).first()
    if config:
        return {
            "title": config.title,
            "subtitle": config.subtitle,
            "welcome_message": config.welcome_message,
            "about_us": config.about_us,
            "hero_image_url": config.hero_image_url,
            "sponsors": config.sponsors,
        }
    return None


# ==================== Course Detail View Operations ====================


@cached(
    cache_key="",
    ttl=CACHE_TTL["course"],
    key_builder=lambda db, course_id, skip, limit: f"course:list:{skip}:{limit}",
)
def get_courses(
    db: Session,
    skip: int = None,
    limit: int = None,
) -> Tuple[list[CourseDetailView], int]:
    """Get list of all courses with pagination.

    Returns:
        List of course details ordered by name
    """
    query = db.query(CourseDetailView).order_by(CourseDetailView.name.asc())
    total = query.count()

    return query.offset(skip).limit(limit).all(), total
