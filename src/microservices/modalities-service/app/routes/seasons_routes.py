import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from taca_events.pydantic_schemas.modalities import (
    ModalityTypeCreatedData,
    ModalityTypeCreatedV1,
    SeasonCreatedData,
    SeasonCreatedV1,
    TeamCreatedData,
    TeamCreatedV1,
    _EscalaoData,
)

from ..database import get_db_session
from ..logger import logger
from ..models import (
    Course,
    ModalityType,
    Nucleo,
    Season,
    SeasonModality,
    Staff,
    Student,
    Team,
)
from ..outbox_publisher import outbox_publisher
from ..schemas import SeasonCreate, SeasonResponse, SeasonSummaryResponse
from ..utils import get_active_season

router = APIRouter()


@router.get("/seasons", response_model=List[SeasonResponse])
def get_seasons(db: Session = Depends(get_db_session)):
    """
    Retrieve all seasons with their associated modalities and modality types.
    """
    try:
        seasons = db.query(Season).all()
        return [s.to_dict() for s in seasons]
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database integrity error",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.post(
    "/seasons", response_model=SeasonResponse, status_code=status.HTTP_201_CREATED
)
def create_season(season_payload: SeasonCreate, db: Session = Depends(get_db_session)):
    """
    Create a new season with the provided details.
    """
    try:
        # Update the current active season to inactive if it exists
        current_season = get_active_season(db)
        current_season.finished_at = datetime.now(timezone.utc)
        current_season.finished_by = season_payload.admin_id
        db.flush()  # Flush to save the changes to the current season

        # Create new season instance
        new_season = Season(
            name=season_payload.name, created_by=season_payload.admin_id
        )
        db.add(new_season)
        db.flush()  # Flush to get the new season ID

        # Copy current ModalityTypes and Teams from the most recent season if it exists
        modality_types_to_map = {}
        for modality_type in current_season.season_modality_types:
            new_modality_type = ModalityType(
                name=modality_type.name,
                description=modality_type.description,
                mode=modality_type.mode,
                escaloes=modality_type.escaloes,
                tournament_competitor_type=modality_type.tournament_competitor_type,
                season_id=new_season.id,
                created_by=season_payload.admin_id,
            )
            db.add(new_modality_type)
            db.flush()  # Flush to get the new modality type ID

            # Emit event via outbox
            event = ModalityTypeCreatedV1.create(
                aggregate_id=new_modality_type.id,
                data=ModalityTypeCreatedData(
                    season_id=new_season.id,
                    modality_type_id=new_modality_type.id,
                    name=new_modality_type.name,
                    description=new_modality_type.description,
                    mode=new_modality_type.mode,
                    escaloes=[
                        _EscalaoData(
                            min_participants=e["minParticipants"],
                            max_participants=e["maxParticipants"],
                            points=e["points"],
                            name=e["escalao"],
                        )
                        for e in modality_type.escaloes
                    ],
                ),
            )
            outbox_publisher.emit_event(
                db=db,
                event_type=event.event_type(),
                aggregate_type=event.aggregate_type(),
                aggregate_id=new_modality_type.id,
                data=event.to_data_dict(),
            )

            modality_types_to_map[modality_type.id] = new_modality_type.id
        db.flush()  # Flush to save the new modality types
        for team in current_season.season_teams:
            new_team = Team(
                modality_id=team.modality_id,
                course_id=team.course_id,
                name=team.name,
                season_id=new_season.id,
                created_by=season_payload.admin_id,
                derived_from_team_id=team.id,  # Track lineage of teams across seasons
            )
            db.add(new_team)
            db.flush()  # Flush to save the new teams

            # Emit event via outbox
            event = TeamCreatedV1.create(
                aggregate_id=new_team.id,
                data=TeamCreatedData(
                    team_id=new_team.id,
                    name=new_team.name,
                    modality_id=new_team.modality_id,
                    course_id=new_team.course_id,
                    season_id=new_season.id,
                ),
            )
            outbox_publisher.emit_event(
                db=db,
                event_type=event.event_type(),
                aggregate_type=event.aggregate_type(),
                aggregate_id=new_team.id,
                data=event.to_data_dict(),
            )

        # Create an entry associating Modalities and Courses with the new season
        for modality in current_season.season_modalities:
            new_season_modality = SeasonModality(
                season_id=new_season.id,
                modality_id=modality.modality_id,
                modality_type_id=modality_types_to_map.get(
                    modality.modality_type_id
                ),  # Map old modality type ID to new one
            )
            db.add(new_season_modality)
        db.flush()  # Flush to save the new season modalities

        for course in current_season.season_courses:
            new_season.season_courses.append(course)
        db.flush()  # Flush to save the new season courses

        aggregate_id = uuid.uuid4()
        event = SeasonCreatedV1.create(
            aggregate_id=aggregate_id,
            data=SeasonCreatedData(
                season_id=new_season.id,
                name=new_season.name,
            ),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type=event.aggregate_type(),
            aggregate_id=aggregate_id,
            data=event.to_data_dict(),
        )

        db.commit()
        return new_season.to_dict()

    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Season with the same name already exists",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get("/seasons/current", response_model=SeasonResponse)
def get_current_season_route(db: Session = Depends(get_db_session)):
    """
    Retrieve the current active season with its associated modalities and modality types.
    """
    try:
        current_season = get_active_season(db)
        if not current_season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No active season found"
            )
        return current_season.to_dict()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get("/seasons/{season_id}", response_model=SeasonResponse)
def get_season_by_id(season_id: int, db: Session = Depends(get_db_session)):
    """
    Retrieve a specific season by its ID, including its associated modalities and modality types.
    """

    season = db.query(Season).filter(Season.id == season_id).first()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Season not found"
        )
    return season.to_dict()


@router.get("/seasons/{season_id}/summary", response_model=SeasonSummaryResponse)
def get_season_summary(
    season_id: int, admin_id: str | None = None, db: Session = Depends(get_db_session)
):
    """
    Retrieve summary information for a specific season by its ID.
    """
    season_stmt = db.query(Season).filter(Season.id == season_id)
    if not season_stmt.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Season not found"
        )
    base_season = season_stmt.first()

    # Build queries for courses, teams, and athletes, applying admin_id filter if provided
    courses_query = (
        db.query(Course).join(Season.season_courses).filter(Season.id == season_id)
    )
    teams_query = db.query(Team).filter(Team.season_id == season_id)
    athletes_query = db.query(Student).filter(Student.is_member == True)  # noqa: E712
    if admin_id:
        courses_query = courses_query.join(Course.nucleo).filter(
            Nucleo.admins_ids.any(admin_id)
        )
        teams_query = (
            teams_query.join(Team.course)
            .join(Course.nucleo)
            .filter(Nucleo.admins_ids.any(admin_id))
        )
        athletes_query = (
            athletes_query.join(Student.course)
            .join(Course.nucleo)
            .filter(Nucleo.admins_ids.any(admin_id))
        )

    courses_count = courses_query.count()
    teams_count = teams_query.count()
    athletes_count = athletes_query.count()
    staff_count = db.query(Staff).count()

    # Build response object
    resp_obj = SeasonSummaryResponse(
        id=base_season.id,
        name=base_season.name,
        modality_types_count=len(base_season.season_modality_types),
        active_modalities_count=len(base_season.season_modalities),
        active_courses_count=courses_count,
        teams_count=teams_count,
        athletes_count=athletes_count,
        staff_count=staff_count,
    )

    if admin_id:
        resp_obj.admin_courses_ids = [course.id for course in courses_query.all()]
        resp_obj.admin_teams_ids = [team.id for team in teams_query.all()]
        resp_obj.admin_athletes_ids = [athlete.id for athlete in athletes_query.all()]

    return resp_obj
