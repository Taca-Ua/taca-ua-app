from datetime import datetime, timezone
from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from taca_events.pydantic_schemas.modalities import (
    StudentCreatedData,
    StudentCreatedV1,
    StudentDeletedData,
    StudentDeletedV1,
    StudentUpdatedData,
    StudentUpdatedV1,
)

from ..database import get_db_session
from ..logger import logger
from ..models import Course, Nucleo, Student, Team
from ..outbox_publisher import outbox_publisher
from ..schemas import (
    StudentCreate,
    StudentMembershipSyncRequest,
    StudentMembershipSyncResponse,
    StudentResponse,
    StudentUpdate,
)

router = APIRouter()

# Default user ID for operations (replace with actual auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


def _normalize_nmec(raw: str) -> str:
    return raw.strip().lstrip("\ufeff")


def _students_scope_query(db: Session, admin_id: str = None):
    q = db.query(Student)
    if admin_id is not None:
        q = (
            q.join(Student.course)
            .join(Course.nucleo)
            .filter(Nucleo.admins_ids.any(admin_id))
        )
    return q


def _emit_student_is_member_update(
    db: Session, student: Student, is_member: bool
) -> None:
    event = StudentUpdatedV1.create(
        aggregate_id=student.id,
        data=StudentUpdatedData(
            student_id=student.id,
            is_member=is_member,
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="student",
        aggregate_id=student.id,
        data=event.to_data_dict(),
    )


@router.get("/students", response_model=List[StudentResponse])
def list_students(
    admin_id: str = None,
    course_id: str = None,
    team_id: str = None,
    db: Session = Depends(get_db_session),
):
    """List all students"""
    students = db.query(Student)
    if admin_id is not None:
        students = (
            students.join(Student.course)
            .join(Course.nucleo)
            .filter(Nucleo.admins_ids.any(admin_id))
        )
    if course_id is not None:
        students = students.filter(Student.course_id == course_id)
    if team_id is not None:
        students = students.filter(Student.teams.any(Team.id == team_id))
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
        event = StudentCreatedV1.create(
            aggregate_id=student.id,
            data=StudentCreatedData(
                student_id=student.id,
                full_name=student.full_name,
                course_id=student.course_id,
                student_number=student.student_number,
                is_member=student.is_member,
            ),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type="student",
            aggregate_id=student.id,
            data=event.to_data_dict(),
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


@router.post("/students/sync-membership", response_model=StudentMembershipSyncResponse)
def sync_membership(
    body: StudentMembershipSyncRequest,
    admin_id: str = None,
    db: Session = Depends(get_db_session),
):
    """Reset sócio status for all participants in scope, then set sócio for listed NMECs.

    Scope: all students (admin_id omitted) or students whose course belongs to a núcleo
    where the given admin_id is in admins_ids.
    """
    if len(body.student_numbers) > 50_000:
        raise HTTPException(
            status_code=400,
            detail="Too many student numbers in one request (max 50000)",
        )

    nmec_set = set()
    for raw in body.student_numbers:
        n = _normalize_nmec(raw)
        if n:
            nmec_set.add(n)

    students = _students_scope_query(db, admin_id).all()
    in_scope_keys = {_normalize_nmec(s.student_number) for s in students}

    reset_to_non_socio = 0
    set_as_socio = 0
    unmatched = sorted(nmec_set - in_scope_keys)

    now = datetime.now(timezone.utc)
    for student in students:
        key = _normalize_nmec(student.student_number)
        new_member = key in nmec_set
        if student.is_member == new_member:
            continue
        student.is_member = new_member
        student.updated_at = now
        if new_member:
            set_as_socio += 1
        else:
            reset_to_non_socio += 1
        _emit_student_is_member_update(db, student, new_member)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Could not persist student membership sync",
        )

    return StudentMembershipSyncResponse(
        participants_in_scope=len(students),
        reset_to_non_socio=reset_to_non_socio,
        set_as_socio=set_as_socio,
        unmatched_numbers=unmatched,
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
    event = StudentUpdatedV1.create(
        aggregate_id=student.id,
        data=StudentUpdatedData(
            student_id=student.id,
            full_name=changes_made.get("full_name"),
            course_id=changes_made.get("course_id"),
            student_number=changes_made.get("student_number"),
            is_member=changes_made.get("is_member"),
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="student",
        aggregate_id=student.id,
        data=event.to_data_dict(),
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
    event = StudentDeletedV1.create(
        aggregate_id=student.id,
        data=StudentDeletedData(
            student_id=student.id,
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="student",
        aggregate_id=student.id,
        data=event.to_data_dict(),
    )

    db.delete(student)
    db.commit()
    logger.info(f"Deleted student: {student_id}")


@router.post("/students/batch-get", response_model=Dict[str, StudentResponse])
def get_students_by_ids(student_ids: List[UUID], db: Session = Depends(get_db_session)):
    """Get multiple students by their IDs"""
    students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    return {str(student.id): student.to_dict() for student in students}
