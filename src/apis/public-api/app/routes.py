from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import get_db
from .logger import logger

router = APIRouter()

# ==================== Team Endpoints ====================


@router.get(
    "/teams",
    response_model=schemas.TeamDetailList,
    summary="List all teams",
    description="Get a paginated list of teams with optional filters",
)
def list_teams(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    course_id: Optional[UUID] = Query(None, description="Filter by course ID"),
    nucleo_id: Optional[UUID] = Query(None, description="Filter by nucleo ID"),
    modality_id: Optional[UUID] = Query(None, description="Filter by modality ID"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of teams with pagination and optional filters.

    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    - **course_id**: Optional filter by course
    - **nucleo_id**: Optional filter by nucleo
    - **modality_id**: Optional filter by modality
    """
    skip = (page - 1) * page_size
    teams, total = crud.get_teams(
        db=db,
        skip=skip,
        limit=page_size,
        course_id=course_id,
        nucleo_id=nucleo_id,
        modality_id=modality_id,
    )

    logger.info(
        "teams_listed",
        total=total,
        page=page,
        page_size=page_size,
        filters={
            "course_id": str(course_id) if course_id else None,
            "nucleo_id": str(nucleo_id) if nucleo_id else None,
            "modality_id": str(modality_id) if modality_id else None,
        },
    )

    return schemas.TeamDetailList(
        items=teams,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/teams/{team_id}",
    response_model=schemas.TeamDetail,
    summary="Get team by ID",
    description="Get detailed information about a specific team",
)
def get_team(
    team_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve detailed information about a specific team.

    - **team_id**: Unique identifier of the team
    """
    team = crud.get_team_by_id(db=db, team_id=team_id)
    if not team:
        logger.warning("team_not_found", team_id=str(team_id))
        raise HTTPException(status_code=404, detail="Team not found")

    logger.info("team_retrieved", team_id=str(team_id))
    return team


# ==================== Student Endpoints ====================


@router.get(
    "/students",
    response_model=schemas.StudentDetailList,
    summary="List all students",
    description="Get a paginated list of students with optional filters",
)
def list_students(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    course_id: Optional[UUID] = Query(None, description="Filter by course ID"),
    nucleo_id: Optional[UUID] = Query(None, description="Filter by nucleo ID"),
    is_member: Optional[bool] = Query(None, description="Filter by membership status"),
    search: Optional[str] = Query(None, description="Search in student name or number"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of students with pagination and optional filters.

    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    - **course_id**: Optional filter by course
    - **nucleo_id**: Optional filter by nucleo
    - **is_member**: Optional filter by membership status
    - **search**: Optional search in name or student number
    """
    skip = (page - 1) * page_size
    students, total = crud.get_students(
        db=db,
        skip=skip,
        limit=page_size,
        course_id=course_id,
        nucleo_id=nucleo_id,
        is_member=is_member,
        search=search,
    )

    logger.info(
        "students_listed",
        total=total,
        page=page,
        page_size=page_size,
        filters={
            "course_id": str(course_id) if course_id else None,
            "nucleo_id": str(nucleo_id) if nucleo_id else None,
            "is_member": is_member,
            "search": search,
        },
    )

    return schemas.StudentDetailList(
        items=students,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/students/{student_id}",
    response_model=schemas.StudentDetail,
    summary="Get student by ID",
    description="Get detailed information about a specific student",
)
def get_student(
    student_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve detailed information about a specific student.

    - **student_id**: Unique identifier of the student
    """
    student = crud.get_student_by_id(db=db, student_id=student_id)
    if not student:
        logger.warning("student_not_found", student_id=str(student_id))
        raise HTTPException(status_code=404, detail="Student not found")

    logger.info("student_retrieved", student_id=str(student_id))
    return student


@router.get(
    "/students/by-number/{student_number}",
    response_model=schemas.StudentDetail,
    summary="Get student by number",
    description="Get detailed information about a student by their student number",
)
def get_student_by_number(
    student_number: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve detailed information about a student by their student number.

    - **student_number**: Student number
    """
    student = crud.get_student_by_number(db=db, student_number=student_number)
    if not student:
        logger.warning("student_not_found", student_number=student_number)
        raise HTTPException(status_code=404, detail="Student not found")

    logger.info("student_retrieved", student_number=student_number)
    return student


# ==================== Tournament Endpoints ====================


@router.get(
    "/tournaments",
    response_model=schemas.TournamentDetailList,
    summary="List all tournaments",
    description="Get a paginated list of tournaments with optional filters",
)
def list_tournaments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    modality_id: Optional[UUID] = Query(None, description="Filter by modality ID"),
    status: Optional[str] = Query(None, description="Filter by tournament status"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of tournaments with pagination and optional filters.

    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    - **modality_id**: Optional filter by modality
    - **status**: Optional filter by status (draft, active, finished, cancelled)
    """
    skip = (page - 1) * page_size
    tournaments, total = crud.get_tournaments(
        db=db,
        skip=skip,
        limit=page_size,
        modality_id=modality_id,
        status=status,
    )

    logger.info(
        "tournaments_listed",
        total=total,
        page=page,
        page_size=page_size,
        filters={
            "modality_id": str(modality_id) if modality_id else None,
            "status": status,
        },
    )

    return schemas.TournamentDetailList(
        items=tournaments,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/tournaments/{tournament_id}",
    response_model=schemas.TournamentDetail,
    summary="Get tournament by ID",
    description="Get detailed information about a specific tournament",
)
def get_tournament(
    tournament_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve detailed information about a specific tournament.

    - **tournament_id**: Unique identifier of the tournament
    """
    tournament = crud.get_tournament_by_id(db=db, tournament_id=tournament_id)
    if not tournament:
        logger.warning("tournament_not_found", tournament_id=str(tournament_id))
        raise HTTPException(status_code=404, detail="Tournament not found")

    logger.info("tournament_retrieved", tournament_id=str(tournament_id))
    return tournament


@router.get(
    "/tournaments/{tournament_id}/standings",
    response_model=schemas.TournamentStandingsList,
    summary="Get tournament standings",
    description="Get the current standings/rankings for a tournament",
)
def get_tournament_standings(
    tournament_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Retrieve the current standings for a specific tournament.

    Results are ordered by rank (ascending).

    - **tournament_id**: Unique identifier of the tournament
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    """
    # First check if tournament exists
    tournament = crud.get_tournament_by_id(db=db, tournament_id=tournament_id)
    if not tournament:
        logger.warning("tournament_not_found", tournament_id=str(tournament_id))
        raise HTTPException(status_code=404, detail="Tournament not found")

    skip = (page - 1) * page_size
    standings, total = crud.get_tournament_standings(
        db=db,
        tournament_id=tournament_id,
        skip=skip,
        limit=page_size,
    )

    logger.info(
        "tournament_standings_retrieved",
        tournament_id=str(tournament_id),
        total=total,
        page=page,
        page_size=page_size,
    )

    return schemas.TournamentStandingsList(
        items=standings,
        total=total,
        page=page,
        page_size=page_size,
    )


# ==================== Match Endpoints ====================


@router.get(
    "/matches",
    response_model=schemas.MatchDetailList,
    summary="List all matches",
    description="Get a paginated list of matches with optional filters",
)
def list_matches(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    tournament_id: Optional[UUID] = Query(None, description="Filter by tournament ID"),
    status: Optional[str] = Query(None, description="Filter by match status"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of matches with pagination and optional filters.

    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    - **tournament_id**: Optional filter by tournament
    - **status**: Optional filter by status (scheduled, in_progress, completed, finished, cancelled)
    """
    skip = (page - 1) * page_size
    matches, total = crud.get_matches(
        db=db,
        skip=skip,
        limit=page_size,
        tournament_id=tournament_id,
        status=status,
    )

    logger.info(
        "matches_listed",
        total=total,
        page=page,
        page_size=page_size,
        filters={
            "tournament_id": str(tournament_id) if tournament_id else None,
            "status": status,
        },
    )

    return schemas.MatchDetailList(
        items=matches,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/matches/{match_id}",
    response_model=schemas.MatchDetail,
    summary="Get match by ID",
    description="Get detailed information about a specific match",
)
def get_match(
    match_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve detailed information about a specific match.

    Includes participants, results, and statistics.

    - **match_id**: Unique identifier of the match
    """
    match = crud.get_match_by_id(db=db, match_id=match_id)
    if not match:
        logger.warning("match_not_found", match_id=str(match_id))
        raise HTTPException(status_code=404, detail="Match not found")

    logger.info("match_retrieved", match_id=str(match_id))
    return match


# ==================== Competitor Standings Endpoint ====================


@router.get(
    "/competitors/{competitor_id}/standings",
    response_model=list[schemas.TournamentStanding],
    summary="Get competitor standings",
    description="Get all tournament standings for a specific competitor (team or athlete)",
)
def get_competitor_standings(
    competitor_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve all tournament standings for a specific competitor.

    This can be used to see all tournaments a team or athlete has participated in
    and their performance across those tournaments.

    - **competitor_id**: Unique identifier of the competitor (team_id or student_id)
    """
    standings = crud.get_standings_by_competitor(
        db=db,
        competitor_entity_id=competitor_id,
    )

    logger.info(
        "competitor_standings_retrieved",
        competitor_id=str(competitor_id),
        count=len(standings),
    )

    return standings


# ==================== General Ranking Endpoints ====================


@router.get(
    "/ranking/general",
    response_model=schemas.GeneralRankingList,
    summary="Get general ranking",
    description="Get the general ranking of all courses based on tournament performance",
)
def get_general_ranking(
    nucleo_id: Optional[UUID] = Query(None, description="Optional filter by nucleo ID"),
    db: Session = Depends(get_db),
):
    """
    Retrieve the general ranking of courses.

    The ranking is calculated based on points earned in tournaments.
    Points are awarded based on final positions in tournaments according to
    the modality type's escaloes configuration.

    - **nucleo_id**: Optional filter to show ranking only for a specific nucleo
    """
    rankings, total = crud.get_general_ranking(db=db, nucleo_id=nucleo_id)

    logger.info(
        "general_ranking_retrieved",
        total=total,
        filters={"nucleo_id": str(nucleo_id) if nucleo_id else None},
    )

    return schemas.GeneralRankingList(
        items=rankings,
        total=total,
    )


@router.get(
    "/ranking/general/course/{course_id}",
    response_model=schemas.GeneralRanking,
    summary="Get course ranking",
    description="Get ranking information for a specific course",
)
def get_course_ranking(
    course_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve ranking information for a specific course.

    - **course_id**: Unique identifier of the course
    """
    ranking = crud.get_course_ranking(db=db, course_id=course_id)
    if not ranking:
        logger.warning("course_ranking_not_found", course_id=str(course_id))
        raise HTTPException(status_code=404, detail="Course ranking not found")

    logger.info("course_ranking_retrieved", course_id=str(course_id))
    return ranking


# ==================== Modality Ranking Endpoints ====================


@router.get(
    "/ranking/modality",
    response_model=schemas.ModalityRankingList,
    summary="Get modality rankings",
    description=(
        "Get rankings of courses per modality based on tournament performance. "
        "You can optionally filter by modality or nucleo."
    ),
)
def get_modality_ranking(
    modality_id: Optional[UUID] = Query(
        None, description="Optional filter by modality ID"
    ),
    nucleo_id: Optional[UUID] = Query(None, description="Optional filter by nucleo ID"),
    db: Session = Depends(get_db),
):
    """Retrieve rankings of courses within modalities.

    The ranking is calculated based on points earned in tournaments for each
    modality separately. Rankings are ordered by rank and points.

    - **modality_id**: Optional filter to show ranking only for a specific modality
    - **nucleo_id**: Optional filter to show ranking only for a specific nucleo
    """
    rankings, total = crud.get_modality_ranking(
        db=db,
        modality_id=modality_id,
        nucleo_id=nucleo_id,
    )

    logger.info(
        "modality_ranking_retrieved",
        total=total,
        filters={
            "modality_id": str(modality_id) if modality_id else None,
            "nucleo_id": str(nucleo_id) if nucleo_id else None,
        },
    )

    return schemas.ModalityRankingList(
        items=rankings,
        total=total,
    )


@router.get(
    "/ranking/modality/course/{course_id}",
    response_model=list[schemas.ModalityRanking],
    summary="Get course modality rankings",
    description="Get modality-specific ranking information for a given course",
)
def get_course_modality_rankings(
    course_id: UUID,
    db: Session = Depends(get_db),
):
    """Retrieve modality rankings for a specific course.

    Returns one entry per modality in which the course has points.

    - **course_id**: Unique identifier of the course
    """
    rankings = crud.get_course_modality_rankings(db=db, course_id=course_id)

    logger.info(
        "course_modality_rankings_retrieved",
        course_id=str(course_id),
        count=len(rankings),
    )

    return rankings
