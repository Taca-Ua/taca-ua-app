from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from taca_events import EventType

from ..database import get_db_session
from ..event_helpers import emit_event
from ..logger import logger
from ..models import Course, Nucleo
from ..schemas import CourseCreate, CourseResponse, CourseUpdate

router = APIRouter()

# Default user ID for operations (replace with actual auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


@router.get("/courses", response_model=List[CourseResponse])
def list_courses(db: Session = Depends(get_db_session)):
    """List all courses"""
    courses = db.query(Course).all()
    return [course.to_dict() for course in courses]


@router.post(
    "/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED
)
def create_course(course_data: CourseCreate, db: Session = Depends(get_db_session)):
    """Create a new course"""
    # Validate nucleo exists
    nucleo = db.query(Nucleo).filter(Nucleo.id == course_data.nucleo_id).first()
    if not nucleo:
        raise HTTPException(status_code=404, detail="Nucleo not found")

    try:
        course = Course(
            name=course_data.name,
            abbreviation=course_data.abbreviation,
            nucleo_id=course_data.nucleo_id,
            created_by=DEFAULT_USER_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(course)
        db.flush()

        # Emit event via outbox
        emit_event(
            db=db,
            event_type=EventType.COURSE_CREATED,
            aggregate_type="course",
            aggregate_id=course.id,
            data={
                "course_id": str(course.id),
                "nucleo_id": str(course.nucleo_id),
                "name": course.name,
                "abbreviation": course.abbreviation,
            },
        )

        db.commit()
        db.refresh(course)
        logger.info(f"Created course: {course.id}")
        return course.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Course with this abbreviation already exists"
        )


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: UUID, db: Session = Depends(get_db_session)):
    """Get a course by ID"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.to_dict()


@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: UUID, course_data: CourseUpdate, db: Session = Depends(get_db_session)
):
    """Update a course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course_data.name is not None:
        course.name = course_data.name
    if course_data.abbreviation is not None:
        course.abbreviation = course_data.abbreviation
    if course_data.nucleo_id is not None:
        nucleo = db.query(Nucleo).filter(Nucleo.id == course_data.nucleo_id).first()
        if not nucleo:
            raise HTTPException(status_code=404, detail="Nucleo not found")
        course.nucleo_id = course_data.nucleo_id
    course.updated_at = datetime.now(timezone.utc)

    try:
        # Emit event via outbox
        emit_event(
            db=db,
            event_type=EventType.COURSE_UPDATED,
            aggregate_type="course",
            aggregate_id=course.id,
            data={
                "course_id": str(course.id),
                "changes": {
                    "name": course.name,
                    "abbreviation": course.abbreviation,
                    "nucleo_id": str(course.nucleo_id),
                },
            },
        )

        db.commit()
        db.refresh(course)
        logger.info(f"Updated course: {course.id}")
        return course.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Course with this abbreviation already exists"
        )


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Emit event via outbox before deleting
    emit_event(
        db=db,
        event_type=EventType.COURSE_DELETED,
        aggregate_type="course",
        aggregate_id=course.id,
        data={
            "course_id": str(course.id),
        },
    )

    db.delete(course)
    db.commit()
    logger.info(f"Deleted course: {course_id}")
