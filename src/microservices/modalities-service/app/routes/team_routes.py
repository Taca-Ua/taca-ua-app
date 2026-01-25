from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from taca_events import EventType

from ..database import get_db_session
from ..event_helpers import emit_event
from ..logger import logger
from ..models import Course, Modality, Student, Team
from ..schemas import TeamCreate, TeamResponse, TeamUpdate

router = APIRouter()

# Default user ID for operations (replace with actual auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


@router.get("/teams", response_model=List[TeamResponse])
def list_teams(db: Session = Depends(get_db_session)):
    """List all teams"""
    teams = db.query(Team).all()
    return [team.to_dict() for team in teams]


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(team_data: TeamCreate, db: Session = Depends(get_db_session)):
    """Create a new team"""
    # Validate modality exists
    modality = db.query(Modality).filter(Modality.id == team_data.modality_id).first()
    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    # Validate course exists
    course = db.query(Course).filter(Course.id == team_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    team = Team(
        name=team_data.name,
        modality_id=team_data.modality_id,
        course_id=team_data.course_id,
        created_by=DEFAULT_USER_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(team)
    db.flush()

    # Emit event via outbox
    emit_event(
        db=db,
        event_type=EventType.TEAM_CREATED,
        aggregate_type="team",
        aggregate_id=team.id,
        data={
            "team_id": str(team.id),
            "name": team.name,
            "modality_id": str(team.modality_id),
            "course_id": str(team.course_id),
        },
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
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if team_data.name is not None:
        team.name = team_data.name
    if team_data.modality_id is not None:
        modality = (
            db.query(Modality).filter(Modality.id == team_data.modality_id).first()
        )
        if not modality:
            raise HTTPException(status_code=404, detail="Modality not found")
        team.modality_id = team_data.modality_id
    if team_data.course_id is not None:
        course = db.query(Course).filter(Course.id == team_data.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        team.course_id = team_data.course_id

    # Handle adding/removing players
    if team_data.players_add:
        for player_id in team_data.players_add:
            student = db.query(Student).filter(Student.id == player_id).first()
            if student and student not in team.players:
                team.players.append(student)
                # Emit player added event
                emit_event(
                    db=db,
                    event_type=EventType.TEAM_PLAYER_ADDED,
                    aggregate_type="team",
                    aggregate_id=team.id,
                    data={"team_id": str(team.id), "student_id": str(player_id)},
                )

    if team_data.players_remove:
        for player_id in team_data.players_remove:
            student = db.query(Student).filter(Student.id == player_id).first()
            if student and student in team.players:
                team.players.remove(student)
                # Emit player removed event
                emit_event(
                    db=db,
                    event_type=EventType.TEAM_PLAYER_REMOVED,
                    aggregate_type="team",
                    aggregate_id=team.id,
                    data={"team_id": str(team.id), "student_id": str(player_id)},
                )

    team.updated_at = datetime.now(timezone.utc)

    # Emit team updated event
    emit_event(
        db=db,
        event_type=EventType.TEAM_UPDATED,
        aggregate_type="team",
        aggregate_id=team.id,
        data={
            "team_id": str(team.id),
            "changes": {
                "name": team_data.name,
                "modality_id": str(team_data.modality_id),
                "course_id": str(team_data.course_id),
            },
        },
    )

    db.commit()
    db.refresh(team)
    logger.info(f"Updated team: {team.id}")
    return team.to_dict(include_players=True)


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Emit team deleted event before deletion
    emit_event(
        db=db,
        event_type=EventType.TEAM_DELETED,
        aggregate_type="team",
        aggregate_id=team.id,
        data={"team_id": str(team.id)},
    )

    db.delete(team)
    db.commit()
    logger.info(f"Deleted team: {team_id}")


@router.post("/teams/batch-get", response_model=List[TeamResponse])
def get_teams_by_ids(team_ids: List[UUID], db: Session = Depends(get_db_session)):
    """Get multiple teams by their IDs"""
    teams = db.query(Team).filter(Team.id.in_(team_ids)).all()
    return [team.to_dict(include_players=True) for team in teams]
