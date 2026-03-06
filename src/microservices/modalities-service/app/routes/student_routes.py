from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from taca_events import EventType

from ..database import get_db_session
from ..logger import logger
from ..models import Course, Nucleo, Student
from ..outbox_publisher import outbox_publisher
from ..schemas import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter()

# Default user ID for operations (replace with actual auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


@router.get("/students", response_model=List[StudentResponse])
def list_students(admin_id: str = None, db: Session = Depends(get_db_session)):
    """List all students"""
    students = db.query(Student)
    if admin_id is not None:
        students = (
            students.join(Student.course)
            .join(Course.nucleo)
            .filter(Nucleo.admins_ids.any(admin_id))
        )
    students = students.all()
    return [student.to_dict() for student in students]


@router.post(
    "/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED
)
def create_student(student_data: StudentCreate, db: Session = Depends(get_db_session)):
    """Create a new student"""
    # Validate course exists
    course = db.query(Course).filter(Course.id == student_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    try:
        student = Student(
            full_name=student_data.full_name,
            course_id=student_data.course_id,
            student_number=student_data.student_number,
            is_member=student_data.is_member,
            created_by=DEFAULT_USER_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(student)
        db.flush()

        # Emit event via outbox
        outbox_publisher.emit_event(
            db=db,
            event_type=EventType.STUDENT_CREATED,
            aggregate_type="student",
            aggregate_id=student.id,
            data={
                "student_id": str(student.id),
                "full_name": student.full_name,
                "course_id": str(student.course_id),
                "student_number": student.student_number,
                "is_member": student.is_member,
            },
        )

        db.commit()
        db.refresh(student)
        logger.info(f"Created student: {student.id}")
        return student.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Student with this student number already exists"
        )


@router.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: UUID, db: Session = Depends(get_db_session)):
    """Get a student by ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student.to_dict()


@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: UUID, student_data: StudentUpdate, db: Session = Depends(get_db_session)
):
    """Update a student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    changes_made = {}
    if student_data.full_name is not None:
        student.full_name = student_data.full_name
        changes_made["full_name"] = student_data.full_name
    if student_data.course_id is not None:
        course = db.query(Course).filter(Course.id == student_data.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        student.course_id = student_data.course_id
        changes_made["course_id"] = student_data.course_id
    if student_data.student_number is not None:
        student.student_number = student_data.student_number
        changes_made["student_number"] = student_data.student_number
    if student_data.is_member is not None:
        student.is_member = student_data.is_member
        changes_made["is_member"] = student_data.is_member
    student.updated_at = datetime.now(timezone.utc)

    # Emit event via outbox
    outbox_publisher.emit_event(
        db=db,
        event_type=EventType.STUDENT_UPDATED,
        aggregate_type="student",
        aggregate_id=student.id,
        data={
            "student_id": str(student.id),
            **{
                k: v
                for k, v in changes_made.items()
                if k in ["full_name", "course_id", "student_number", "is_member"]
            },
        },
    )

    try:
        db.commit()
        db.refresh(student)
        logger.info(f"Updated student: {student.id}")
        return student.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Student with this student number already exists"
        )


@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Emit event via outbox before deletion
    outbox_publisher.emit_event(
        db=db,
        event_type=EventType.STUDENT_DELETED,
        aggregate_type="student",
        aggregate_id=student.id,
        data={
            "student_id": str(student.id),
        },
    )

    db.delete(student)
    db.commit()
    logger.info(f"Deleted student: {student_id}")


@router.post("/students/batch-get", response_model=List[StudentResponse])
def get_students_by_ids(student_ids: List[UUID], db: Session = Depends(get_db_session)):
    """Get multiple students by their IDs"""
    students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    return [student.to_dict() for student in students]
