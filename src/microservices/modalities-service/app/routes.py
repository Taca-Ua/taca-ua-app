"""
API routes for Modalities Service.
Handles modalities, teams, and students.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from . import schemas
from .database import get_db_session
from .events import (
    publish_modality_created,
    publish_modality_deleted,
    publish_modality_updated,
    publish_student_created,
    publish_team_created,
    publish_team_deleted,
    publish_team_updated,
)
from .models import Modality, ModalityType, Student, Team

router = APIRouter()


@router.post("/modalities", response_model=schemas.ModalityResponse, status_code=201)
def create_modality(
    modality_data: schemas.ModalityCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Create a new modality."""
    try:
        modality_type = ModalityType(modality_data.type)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid modality type: {modality_data.type}"
        )

    modality = Modality(
        name=modality_data.name,
        type=modality_type,
        scoring_schema=modality_data.scoring_schema,
        created_by=modality_data.created_by,
    )

    db.add(modality)
    db.commit()
    db.refresh(modality)

    background_tasks.add_task(publish_modality_created, modality_data)
    return modality


@router.put("/modalities/{modality_id}", response_model=schemas.ModalityResponse)
def update_modality(
    modality_id: UUID,
    modality_data: schemas.ModalityUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Update a modality."""
    modality = db.query(Modality).filter(Modality.id == modality_id).first()

    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    if modality_data.name is not None:
        modality.name = modality_data.name
    if modality_data.type is not None:
        try:
            modality.type = ModalityType(modality_data.type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid modality type: {modality_data.type}"
            )
    if modality_data.scoring_schema is not None:
        modality.scoring_schema = modality_data.scoring_schema

    modality.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(modality)

    background_tasks.add_task(publish_modality_updated, modality_data, {})
    return modality


@router.delete("/modalities/{modality_id}", status_code=204)
def delete_modality(
    modality_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Delete a modality."""

    modality = db.query(Modality).filter(Modality.id == modality_id).first()

    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    # Check if there are teams or tournaments associated
    team_count = db.query(Team).filter(Team.modality_id == modality_id).count()
    if team_count > 0:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete modality with associated teams",
        )

    db.delete(modality)
    db.commit()

    background_tasks.add_task(publish_modality_deleted, modality_id)
    return None


@router.get("/modalities/{modality_id}", response_model=schemas.ModalityResponse)
def get_modality(modality_id: UUID, db: Session = Depends(get_db_session)):
    """Get a modality by ID."""
    modality = db.query(Modality).filter(Modality.id == modality_id).first()

    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    return modality


@router.get("/modalities")
def list_modalities(
    type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
):
    """List modalities with optional filters."""
    query = db.query(Modality)

    if type:
        try:
            modality_type = ModalityType(type)
            query = query.filter(Modality.type == modality_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid modality type: {type}"
            )

    total = query.count()
    modalities = query.offset(offset).limit(limit).all()

    return {
        "modalities": modalities,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/teams", response_model=schemas.TeamResponse, status_code=201)
def create_team(
    team_data: schemas.TeamCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Create a new team."""
    # Verify modality exists and type allows teams
    modality = db.query(Modality).filter(Modality.id == team_data.modality_id).first()
    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    if modality.type == ModalityType.INDIVIDUAL:
        raise HTTPException(
            status_code=422,
            detail="Cannot create team for individual modality",
        )

    # Generate team name if not provided
    if not team_data.name:
        # Simple auto-generation logic
        team_count = (
            db.query(Team)
            .filter(
                Team.modality_id == team_data.modality_id,
                Team.course_id == team_data.course_id,
            )
            .count()
        )
        team_data.name = f"Team {team_count + 1}"

    # Verify players belong to the same course
    if team_data.players:
        students = db.query(Student).filter(Student.id.in_(team_data.players)).all()
        if len(students) != len(team_data.players):
            raise HTTPException(status_code=404, detail="One or more players not found")

        if any(s.course_id != team_data.course_id for s in students):
            raise HTTPException(
                status_code=422,
                detail="All players must belong to the same course",
            )

    team = Team(
        modality_id=team_data.modality_id,
        course_id=team_data.course_id,
        name=team_data.name,
        players=team_data.players,
        created_by=team_data.created_by,
    )

    db.add(team)
    db.commit()
    db.refresh(team)

    background_tasks.add_task(publish_team_created, team_data)
    return team


@router.put("/teams/{team_id}", response_model=schemas.TeamResponse)
def update_team(
    team_id: UUID,
    team_data: schemas.TeamUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Update a team."""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # TODO: Check if team is in active tournament

    if team_data.name is not None:
        team.name = team_data.name

    current_players = team.players or []

    if team_data.players_add:
        # Verify players exist and belong to same course
        students = db.query(Student).filter(Student.id.in_(team_data.players_add)).all()
        if len(students) != len(team_data.players_add):
            raise HTTPException(status_code=404, detail="One or more players not found")

        if any(s.course_id != team.course_id for s in students):
            raise HTTPException(
                status_code=422,
                detail="All players must belong to the same course",
            )

        current_players = list(set(current_players + team_data.players_add))

    if team_data.players_remove:
        current_players = [
            p for p in current_players if p not in team_data.players_remove
        ]

    team.players = current_players
    team.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(team)

    background_tasks.add_task(publish_team_updated, team_data, {})
    return team


@router.delete("/teams/{team_id}", status_code=204)
def delete_team(
    team_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Delete a team."""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # TODO: Check if team is in active tournament

    db.delete(team)
    db.commit()

    background_tasks.add_task(publish_team_deleted, team_id)
    return None


@router.get("/teams/{team_id}", response_model=schemas.TeamResponse)
def get_team(team_id: UUID, db: Session = Depends(get_db_session)):
    """Get a team by ID."""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return team


@router.get("/teams")
def list_teams(
    modality_id: Optional[UUID] = Query(None),
    course_id: Optional[UUID] = Query(None),
    tournament_id: Optional[UUID] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
):
    """List teams with optional filters."""
    query = db.query(Team)

    if modality_id:
        query = query.filter(Team.modality_id == modality_id)
    if course_id:
        query = query.filter(Team.course_id == course_id)
    # tournament_id filter would require checking tournament-team associations

    total = query.count()
    teams = query.offset(offset).limit(limit).all()

    return {
        "teams": teams,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/students", response_model=schemas.StudentResponse, status_code=201)
def create_student(
    student_data: schemas.StudentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Create a new student."""
    # Check if student_number already exists
    existing = (
        db.query(Student)
        .filter(Student.student_number == student_data.student_number)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Student with number {student_data.student_number} already exists",
        )

    student = Student(
        course_id=student_data.course_id,
        full_name=student_data.full_name,
        student_number=student_data.student_number,
        email=student_data.email,
        is_member=student_data.is_member or False,
        created_by=student_data.created_by,
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    background_tasks.add_task(publish_student_created, student_data)
    return student


@router.put("/students/{student_id}", response_model=schemas.StudentResponse)
def update_student(
    student_id: UUID,
    student_data: schemas.StudentUpdate,
    db: Session = Depends(get_db_session),
):
    """Update a student."""
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if student_data.full_name is not None:
        student.full_name = student_data.full_name
    if student_data.email is not None:
        student.email = student_data.email
    if student_data.is_member is not None:
        student.is_member = student_data.is_member

    student.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(student)

    return student


@router.get("/students/{student_id}", response_model=schemas.StudentResponse)
def get_student(student_id: UUID, db: Session = Depends(get_db_session)):
    """Get a student by ID."""
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@router.get("/students")
def list_students(
    course_id: Optional[UUID] = Query(None),
    is_member: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
):
    """List students with optional filters."""
    query = db.query(Student)

    if course_id:
        query = query.filter(Student.course_id == course_id)
    if is_member is not None:
        query = query.filter(Student.is_member == is_member)
    if search:
        query = query.filter(
            (Student.full_name.ilike(f"%{search}%"))
            | (Student.student_number.ilike(f"%{search}%"))
        )

    total = query.count()
    students = query.offset(offset).limit(limit).all()

    return {
        "students": students,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
