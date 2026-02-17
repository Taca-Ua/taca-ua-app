"""
Internal API endpoints for Modalities Service.

This module provides internal-only endpoints for:
- Snapshot data for read model rebuilds
- Health checks
- Administrative operations

These endpoints should NOT be exposed via API Gateway.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db_session
from .logger import logger
from .models import (
    Course,
    Modality,
    ModalityType,
    Nucleo,
    Staff,
    Student,
    Team,
    team_players,
)

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/snapshot")
def get_snapshot(db: Session = Depends(get_db_session)):
    """
    Return complete snapshot of all modalities data.

    This endpoint is used by the Read Model Updater to rebuild projections.
    Returns all nucleos, courses, modality types, modalities, students,
    staff, teams, and team-player relationships.

    **IMPORTANT**: This endpoint should be internal-only and NOT exposed
    via API Gateway. Only accessible within Docker network.

    Returns:
        JSON object with all modalities domain data:
        - nucleos: List of all nucleos
        - courses: List of all courses
        - modality_types: List of all modality types
        - modalities: List of all modalities
        - students: List of all students
        - staff: List of all staff members
        - teams: List of all teams
        - team_players: List of all team-player relationships
    """
    logger.info("snapshot_requested", service="modalities")

    try:
        # Fetch all domain data
        nucleos = db.query(Nucleo).all()
        courses = db.query(Course).all()
        modality_types = db.query(ModalityType).all()
        modalities = db.query(Modality).all()
        students = db.query(Student).all()
        staff = db.query(Staff).all()
        teams = db.query(Team).all()

        # Fetch team-player relationships from association table
        team_player_relationships = db.execute(team_players.select()).fetchall()

        # Convert to dictionaries
        snapshot = {
            "nucleos": [
                {
                    "id": str(n.id),
                    "name": n.name,
                    "abbreviation": n.abbreviation,
                    "created_by": str(n.created_by),
                    "created_at": n.created_at.isoformat() if n.created_at else None,
                    "updated_at": n.updated_at.isoformat() if n.updated_at else None,
                }
                for n in nucleos
            ],
            "courses": [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "abbreviation": c.abbreviation,
                    "nucleo_id": str(c.nucleo_id),
                    "created_by": str(c.created_by),
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                }
                for c in courses
            ],
            "modality_types": [
                {
                    "id": str(mt.id),
                    "name": mt.name,
                    "description": mt.description,
                    "escaloes": mt.escaloes,
                    "created_by": str(mt.created_by),
                    "created_at": mt.created_at.isoformat() if mt.created_at else None,
                    "updated_at": mt.updated_at.isoformat() if mt.updated_at else None,
                }
                for mt in modality_types
            ],
            "modalities": [
                {
                    "id": str(m.id),
                    "name": m.name,
                    "modality_type_id": str(m.modality_type_id),
                    "created_by": str(m.created_by),
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                    "updated_at": m.updated_at.isoformat() if m.updated_at else None,
                }
                for m in modalities
            ],
            "students": [
                {
                    "id": str(s.id),
                    "full_name": s.full_name,
                    "course_id": str(s.course_id),
                    "student_number": s.student_number,
                    "is_member": s.is_member,
                    "created_by": str(s.created_by),
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                    "updated_at": s.updated_at.isoformat() if s.updated_at else None,
                }
                for s in students
            ],
            "staff": [
                {
                    "id": str(s.id),
                    "full_name": s.full_name,
                    "staff_number": s.staff_number,
                    "contact": s.contact,
                    "created_by": str(s.created_by),
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                    "updated_at": s.updated_at.isoformat() if s.updated_at else None,
                }
                for s in staff
            ],
            "teams": [
                {
                    "id": str(t.id),
                    "modality_id": str(t.modality_id),
                    "course_id": str(t.course_id),
                    "name": t.name,
                    "created_by": str(t.created_by),
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                }
                for t in teams
            ],
            "team_players": [
                {
                    "team_id": str(tp.team_id),
                    "student_id": str(tp.student_id),
                }
                for tp in team_player_relationships
            ],
        }

        logger.info(
            "snapshot_generated",
            service="modalities",
            nucleos_count=len(nucleos),
            courses_count=len(courses),
            modality_types_count=len(modality_types),
            modalities_count=len(modalities),
            students_count=len(students),
            staff_count=len(staff),
            teams_count=len(teams),
            team_players_count=len(team_player_relationships),
        )

        return snapshot

    except Exception as e:
        logger.error("snapshot_generation_failed", service="modalities", error=str(e))
        raise


@router.get("/health")
def health_check():
    """Internal health check endpoint."""
    return {"status": "healthy", "service": "modalities"}
