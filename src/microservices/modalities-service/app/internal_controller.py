"""
Internal API endpoints for Modalities Service.

This module provides internal-only endpoints for:
- Snapshot data for read model rebuilds
- Health checks
- Administrative operations

These endpoints should NOT be exposed via API Gateway.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from taca_snapshots.modalities import (
    CourseSnapshotItem,
    ModalitiesSnapshotResponse,
    ModalitySnapshotItem,
    ModalityTypeSnapshotItem,
    NucleoSnapshotItem,
    StaffSnapshotItem,
    StudentSnapshotItem,
    TeamPlayerSnapshotItem,
    TeamSnapshotItem,
)

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


@router.get("/snapshot", response_model=ModalitiesSnapshotResponse)
def get_snapshot(
    db: Session = Depends(get_db_session),
    limit: int = Query(
        default=10000,
        ge=1,
        le=50000,
        description="Maximum number of records to return per collection",
    ),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
):
    """
    Return complete snapshot of all modalities data as strongly typed DTOs.

    This endpoint is used by the Read Model Updater to rebuild projections.
    Returns all nucleos, courses, modality types, modalities, students,
    staff, teams, and team-player relationships.

    **IMPORTANT**: This endpoint should be internal-only and NOT exposed
    via API Gateway. Only accessible within Docker network.

    Query Parameters:
        limit: Maximum number of records returned per collection (default 10000).
        offset: Number of records to skip (default 0).

    Returns:
        ModalitiesSnapshotResponse with all modalities domain data.
    """
    logger.info("snapshot_requested", service="modalities", limit=limit, offset=offset)

    try:
        # Fetch domain data
        nucleos = db.query(Nucleo).offset(offset).limit(limit).all()
        courses = db.query(Course).offset(offset).limit(limit).all()
        modality_types = db.query(ModalityType).offset(offset).limit(limit).all()
        modalities = db.query(Modality).offset(offset).limit(limit).all()
        students = db.query(Student).offset(offset).limit(limit).all()
        staff = db.query(Staff).offset(offset).limit(limit).all()
        teams = db.query(Team).offset(offset).limit(limit).all()
        team_player_relationships = db.execute(team_players.select()).fetchall()

        # Build typed DTOs
        nucleo_dtos = [
            NucleoSnapshotItem(
                id=str(n.id),
                name=n.name,
                abbreviation=n.abbreviation,
                created_by=str(n.created_by),
                created_at=n.created_at,
                updated_at=n.updated_at,
            )
            for n in nucleos
        ]

        course_dtos = [
            CourseSnapshotItem(
                id=str(c.id),
                name=c.name,
                abbreviation=c.abbreviation,
                nucleo_id=str(c.nucleo_id),
                created_by=str(c.created_by),
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in courses
        ]

        modality_type_dtos = [
            ModalityTypeSnapshotItem(
                id=str(mt.id),
                name=mt.name,
                description=mt.description,
                escaloes=mt.escaloes,
                created_by=str(mt.created_by),
                created_at=mt.created_at,
                updated_at=mt.updated_at,
            )
            for mt in modality_types
        ]

        modality_dtos = [
            ModalitySnapshotItem(
                id=str(m.id),
                name=m.name,
                modality_type_id=str(m.modality_type_id),
                created_by=str(m.created_by),
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in modalities
        ]

        student_dtos = [
            StudentSnapshotItem(
                id=str(s.id),
                full_name=s.full_name,
                course_id=str(s.course_id),
                student_number=s.student_number,
                is_member=s.is_member,
                created_by=str(s.created_by),
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in students
        ]

        staff_dtos = [
            StaffSnapshotItem(
                id=str(s.id),
                full_name=s.full_name,
                staff_number=s.staff_number,
                contact=s.contact,
                created_by=str(s.created_by),
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in staff
        ]

        team_dtos = [
            TeamSnapshotItem(
                id=str(t.id),
                modality_id=str(t.modality_id),
                course_id=str(t.course_id),
                name=t.name,
                created_by=str(t.created_by),
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in teams
        ]

        team_player_dtos = [
            TeamPlayerSnapshotItem(
                team_id=str(tp.team_id),
                student_id=str(tp.student_id),
            )
            for tp in team_player_relationships
        ]

        snapshot = ModalitiesSnapshotResponse(
            nucleos=nucleo_dtos,
            courses=course_dtos,
            modality_types=modality_type_dtos,
            modalities=modality_dtos,
            students=student_dtos,
            staff=staff_dtos,
            teams=team_dtos,
            team_players=team_player_dtos,
        )

        logger.info(
            "snapshot_generated",
            service="modalities",
            nucleos_count=len(nucleo_dtos),
            courses_count=len(course_dtos),
            modality_types_count=len(modality_type_dtos),
            modalities_count=len(modality_dtos),
            students_count=len(student_dtos),
            staff_count=len(staff_dtos),
            teams_count=len(team_dtos),
            team_players_count=len(team_player_dtos),
        )

        return snapshot

    except Exception as e:
        logger.error("snapshot_generation_failed", service="modalities", error=str(e))
        raise


@router.get("/health")
def health_check():
    """Internal health check endpoint."""
    return {"status": "healthy", "service": "modalities"}
