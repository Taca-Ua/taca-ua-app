from datetime import datetime, timezone
from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from taca_events.pydantic_schemas.modalities import (
    TeamCreatedData,
    TeamCreatedV1,
    TeamDeletedData,
    TeamDeletedV1,
    TeamPlayerAddedData,
    TeamPlayerAddedV1,
    TeamPlayerRemovedData,
    TeamPlayerRemovedV1,
    TeamUpdatedData,
    TeamUpdatedV1,
)

from ..database import get_db_session
from ..logger import logger
from ..models import (
    Course,
    Modality,
    Nucleo,
    SeasonModality,
    Student,
    Team,
    season_courses,
)
from ..outbox_publisher import outbox_publisher
from ..schemas import TeamCreate, TeamResponse, TeamUpdate
from ..utils import get_active_season

router = APIRouter()

# Default user ID for operations (replace with actual auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


@router.get("/teams", response_model=List[TeamResponse])
def list_teams(
    season_id: int = None,
    admin_id: str = None,
    modality_id: UUID = None,
    db: Session = Depends(get_db_session),
):
    """List all teams"""
    query = db.query(Team)

    relevant_season_id = season_id
    if season_id is None:
        active_season = get_active_season(db)
        relevant_season_id = active_season.id
    query = query.filter(Team.season_id == relevant_season_id)

    if modality_id:
        query = query.filter(Team.modality_id == modality_id)

    # need to check if the team belongs to a course that belongs to a nucleo managed by the admin_id
    logger.debug(f"Filtering teams for admin_id: {admin_id}")
    if admin_id:
        query = (
            query.join(Team.course)
            .join(Course.nucleo)
            .filter(Nucleo.admins_ids.any(admin_id))
        )

    teams = query.all()
    return [team.to_dict() for team in teams]


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(team_data: TeamCreate, db: Session = Depends(get_db_session)):
    """Create a new team"""
    active_season = get_active_season(db)

    # Validate modality exists for the active season
    modality = (
        db.query(Modality)
        .filter(Modality.id == team_data.modality_id)
        .join(SeasonModality)
        .filter(SeasonModality.season_id == active_season.id)
        .first()
    )
    if not modality:
        raise HTTPException(
            status_code=404, detail="Modality not found for active season"
        )

    # Validate course exists for the active season
    course = (
        db.query(Course)
        .filter(Course.id == team_data.course_id)
        .join(season_courses)
        .filter(season_courses.c.season_id == active_season.id)
        .first()
    )
    if not course:
        raise HTTPException(
            status_code=404, detail="Course not found for active season"
        )

    team = Team(
        name=team_data.name,
        modality_id=team_data.modality_id,
        course_id=team_data.course_id,
        season_id=active_season.id,
        created_by=DEFAULT_USER_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(team)
    db.flush()

    # Emit event via outbox
    event = TeamCreatedV1.create(
        aggregate_id=team.id,
        data=TeamCreatedData(
            team_id=team.id,
            name=team.name,
            modality_id=team.modality_id,
            course_id=team.course_id,
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="team",
        aggregate_id=team.id,
        data=event.to_data_dict(),
    )

    db.commit()
    db.refresh(team)
    logger.info(f"Created team: {team.id}")
    return team.to_dict()


@router.get("/teams/{team_id}", response_model=TeamResponse)
def get_team(team_id: UUID, db: Session = Depends(get_db_session)):
    """Get a team by ID"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.to_dict(include_players=True)


@router.put("/teams/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: UUID, team_data: TeamUpdate, db: Session = Depends(get_db_session)
):
    """Update a team"""
    active_season = get_active_season(db)

    team = (
        db.query(Team)
        .filter(Team.id == team_id, Team.season_id == active_season.id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found for active season")

    changes_made = {}
    if team_data.name is not None:
        team.name = team_data.name
        changes_made["name"] = team_data.name
    if team_data.modality_id is not None:
        modality = (
            db.query(Modality)
            .filter(Modality.id == team_data.modality_id)
            .join(SeasonModality)
            .filter(SeasonModality.season_id == active_season.id)
            .first()
        )
        if not modality:
            raise HTTPException(
                status_code=404, detail="Modality not found for active season"
            )
        team.modality_id = team_data.modality_id
        changes_made["modality_id"] = str(team_data.modality_id)
    if team_data.course_id is not None:
        course = (
            db.query(Course)
            .filter(Course.id == team_data.course_id)
            .join(season_courses)
            .filter(season_courses.c.season_id == active_season.id)
            .first()
        )
        if not course:
            raise HTTPException(
                status_code=404, detail="Course not found for active season"
            )
        team.course_id = team_data.course_id
        changes_made["course_id"] = str(team_data.course_id)

    # Emit team updated event
    event = TeamUpdatedV1.create(
        aggregate_id=team.id,
        data=TeamUpdatedData(
            team_id=team.id,
            name=changes_made.get("name"),
            modality_id=changes_made.get("modality_id"),
            course_id=changes_made.get("course_id"),
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="team",
        aggregate_id=team.id,
        data=event.to_data_dict(exclude_none=True),
    )

    # Handle adding/removing players
    if team_data.players_add:
        for player_id in team_data.players_add:
            student = db.query(Student).filter(Student.id == player_id).first()
            if student and student not in team.players:
                team.players.append(student)
                # Emit player added event
                event = TeamPlayerAddedV1.create(
                    aggregate_id=team.id,
                    data=TeamPlayerAddedData(
                        team_id=team.id,
                        student_id=player_id,
                    ),
                )
                outbox_publisher.emit_event(
                    db=db,
                    event_type=event.event_type(),
                    aggregate_type="team",
                    aggregate_id=team.id,
                    data=event.to_data_dict(),
                )

    if team_data.players_remove:
        for player_id in team_data.players_remove:
            student = db.query(Student).filter(Student.id == player_id).first()
            if student and student in team.players:
                team.players.remove(student)
                # Emit player removed event
                event = TeamPlayerRemovedV1.create(
                    aggregate_id=team.id,
                    data=TeamPlayerRemovedData(
                        team_id=team.id,
                        student_id=player_id,
                    ),
                )
                outbox_publisher.emit_event(
                    db=db,
                    event_type=event.event_type(),
                    aggregate_type="team",
                    aggregate_id=team.id,
                    data=event.to_data_dict(),
                )

    team.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(team)
    logger.info(f"Updated team: {team.id}")
    return team.to_dict(include_players=True)


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a team"""
    active_season = get_active_season(db)

    team = (
        db.query(Team)
        .filter(Team.id == team_id, Team.season_id == active_season.id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found for active season")

    # Emit team deleted event before deletion
    event = TeamDeletedV1.create(
        aggregate_id=team.id,
        data=TeamDeletedData(
            team_id=team.id,
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="team",
        aggregate_id=team.id,
        data=event.to_data_dict(),
    )

    db.delete(team)
    db.commit()
    logger.info(f"Deleted team: {team_id}")


@router.post("/teams/batch-get", response_model=Dict[str, TeamResponse])
def get_teams_by_ids(
    team_ids: List[UUID], admin_id: str = None, db: Session = Depends(get_db_session)
):
    """Get multiple teams by their IDs"""
    teams = db.query(Team).filter(Team.id.in_(team_ids))
    if admin_id:
        teams = (
            teams.join(Team.course)
            .join(Course.nucleo)
            .filter(Nucleo.admins_ids.any(admin_id))
        )
    teams = teams.all()
    return {str(team.id): team.to_dict(include_players=True) for team in teams}
