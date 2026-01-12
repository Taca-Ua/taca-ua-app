"""
FastAPI routes for Modalities Service.
"""

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import get_db_session
from .event_helpers import EventTypes, emit_event
from .logger import logger
from .models import Course, Modality, ModalityType, Nucleo, Staff, Student, Team
from .schemas import (
    CourseCreate,
    CourseResponse,
    CourseUpdate,
    ModalityCreate,
    ModalityResponse,
    ModalityTypeCreate,
    ModalityTypeResponse,
    ModalityTypeUpdate,
    ModalityUpdate,
    NucleoCreate,
    NucleoResponse,
    NucleoUpdate,
    StaffCreate,
    StaffResponse,
    StaffUpdate,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
    TeamCreate,
    TeamResponse,
    TeamUpdate,
)

router = APIRouter()

# Default user ID for operations (replace with actual auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


# ==================== NUCLEO ENDPOINTS ====================
@router.get("/nucleos", response_model=List[NucleoResponse])
def list_nucleos(db: Session = Depends(get_db_session)):
    """List all nucleos"""
    nucleos = db.query(Nucleo).all()
    return [nucleo.to_dict() for nucleo in nucleos]


@router.post(
    "/nucleos", response_model=NucleoResponse, status_code=status.HTTP_201_CREATED
)
def create_nucleo(nucleo_data: NucleoCreate, db: Session = Depends(get_db_session)):
    """Create a new nucleo"""
    try:
        nucleo = Nucleo(
            name=nucleo_data.name,
            abbreviation=nucleo_data.abbreviation,
            created_by=DEFAULT_USER_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(nucleo)
        db.flush()  # Get the ID without committing

        # Emit event via outbox
        emit_event(
            db=db,
            event_type=EventTypes.NUCLEO_CREATED,
            aggregate_type="nucleo",
            aggregate_id=nucleo.id,
            data=nucleo.to_dict(),
        )

        db.commit()
        db.refresh(nucleo)
        logger.info(
            "entity_created",
            entity_type="nucleo",
            entity_id=str(nucleo.id),
            name=nucleo.name,
        )
        return nucleo.to_dict()
    except IntegrityError as e:
        db.rollback()
        logger.error(
            "integrity_error",
            entity_type="nucleo",
            error="duplicate_abbreviation",
            details=str(e),
        )
        raise HTTPException(
            status_code=400, detail="Nucleo with this abbreviation already exists"
        )


@router.get("/nucleos/{nucleo_id}", response_model=NucleoResponse)
def get_nucleo(nucleo_id: UUID, db: Session = Depends(get_db_session)):
    """Get a nucleo by ID"""
    nucleo = db.query(Nucleo).filter(Nucleo.id == nucleo_id).first()
    if not nucleo:
        logger.warning(
            "entity_not_found", entity_type="nucleo", entity_id=str(nucleo_id)
        )
        raise HTTPException(status_code=404, detail="Nucleo not found")
    return nucleo.to_dict()


@router.put("/nucleos/{nucleo_id}", response_model=NucleoResponse)
def update_nucleo(
    nucleo_id: UUID, nucleo_data: NucleoUpdate, db: Session = Depends(get_db_session)
):
    """Update a nucleo"""
    nucleo = db.query(Nucleo).filter(Nucleo.id == nucleo_id).first()
    if not nucleo:
        raise HTTPException(status_code=404, detail="Nucleo not found")

    if nucleo_data.name is not None:
        nucleo.name = nucleo_data.name
    if nucleo_data.abbreviation is not None:
        nucleo.abbreviation = nucleo_data.abbreviation
    nucleo.updated_at = datetime.now(timezone.utc)

    try:
        # Emit event via outbox
        emit_event(
            db=db,
            event_type=EventTypes.NUCLEO_UPDATED,
            aggregate_type="nucleo",
            aggregate_id=nucleo.id,
            data=nucleo.to_dict(),
        )

        db.commit()
        db.refresh(nucleo)
        logger.info(f"Updated nucleo: {nucleo.id}")
        return nucleo.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Nucleo with this abbreviation already exists"
        )


@router.delete("/nucleos/{nucleo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nucleo(nucleo_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a nucleo"""
    nucleo = db.query(Nucleo).filter(Nucleo.id == nucleo_id).first()
    if not nucleo:
        raise HTTPException(status_code=404, detail="Nucleo not found")

    # Emit event via outbox before deleting
    emit_event(
        db=db,
        event_type=EventTypes.NUCLEO_DELETED,
        aggregate_type="nucleo",
        aggregate_id=nucleo.id,
        data={"id": str(nucleo.id), "name": nucleo.name},
    )

    db.delete(nucleo)
    db.commit()
    logger.info(f"Deleted nucleo: {nucleo_id}")


# ==================== COURSE ENDPOINTS ====================
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
            event_type=EventTypes.COURSE_CREATED,
            aggregate_type="course",
            aggregate_id=course.id,
            data=course.to_dict(),
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
            event_type=EventTypes.COURSE_UPDATED,
            aggregate_type="course",
            aggregate_id=course.id,
            data=course.to_dict(),
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
        event_type=EventTypes.COURSE_DELETED,
        aggregate_type="course",
        aggregate_id=course.id,
        data={"id": str(course.id), "name": course.name},
    )

    db.delete(course)
    db.commit()
    logger.info(f"Deleted course: {course_id}")


# ==================== MODALITY TYPE ENDPOINTS ====================
@router.get("/modality-types", response_model=List[ModalityTypeResponse])
def list_modality_types(db: Session = Depends(get_db_session)):
    """List all modality types"""
    modality_types = db.query(ModalityType).all()
    return [mt.to_dict() for mt in modality_types]


@router.post(
    "/modality-types",
    response_model=ModalityTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_modality_type(
    modality_type_data: ModalityTypeCreate, db: Session = Depends(get_db_session)
):
    """Create a new modality type"""
    try:
        modality_type = ModalityType(
            name=modality_type_data.name,
            description=modality_type_data.description,
            escaloes=modality_type_data.escaloes_encoder(),
            created_by=DEFAULT_USER_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(modality_type)
        db.commit()
        db.refresh(modality_type)
        logger.info(f"Created modality type: {modality_type.id}")
        return modality_type.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Modality type with this name already exists"
        )


@router.get("/modality-types/{modality_type_id}", response_model=ModalityTypeResponse)
def get_modality_type(modality_type_id: UUID, db: Session = Depends(get_db_session)):
    """Get a modality type by ID"""
    modality_type = (
        db.query(ModalityType).filter(ModalityType.id == modality_type_id).first()
    )
    if not modality_type:
        raise HTTPException(status_code=404, detail="Modality type not found")
    return modality_type.to_dict()


@router.put("/modality-types/{modality_type_id}", response_model=ModalityTypeResponse)
def update_modality_type(
    modality_type_id: UUID,
    modality_type_data: ModalityTypeUpdate,
    db: Session = Depends(get_db_session),
):
    """Update a modality type"""
    modality_type = (
        db.query(ModalityType).filter(ModalityType.id == modality_type_id).first()
    )
    if not modality_type:
        raise HTTPException(status_code=404, detail="Modality type not found")

    if modality_type_data.name is not None:
        modality_type.name = modality_type_data.name
    if modality_type_data.description is not None:
        modality_type.description = modality_type_data.description
    if modality_type_data.escaloes is not None:
        modality_type.escaloes = modality_type_data.escaloes
    modality_type.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(modality_type)
        logger.info(f"Updated modality type: {modality_type.id}")
        return modality_type.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Modality type with this name already exists"
        )


@router.delete(
    "/modality-types/{modality_type_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_modality_type(modality_type_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a modality type"""
    modality_type = (
        db.query(ModalityType).filter(ModalityType.id == modality_type_id).first()
    )
    if not modality_type:
        raise HTTPException(status_code=404, detail="Modality type not found")

    db.delete(modality_type)
    db.commit()
    logger.info(f"Deleted modality type: {modality_type_id}")


# ==================== MODALITY ENDPOINTS ====================
@router.get("/modalities", response_model=List[ModalityResponse])
def list_modalities(db: Session = Depends(get_db_session)):
    """List all modalities"""
    modalities = db.query(Modality).all()
    return [modality.to_dict() for modality in modalities]


@router.post(
    "/modalities", response_model=ModalityResponse, status_code=status.HTTP_201_CREATED
)
def create_modality(
    modality_data: ModalityCreate, db: Session = Depends(get_db_session)
):
    """Create a new modality"""
    # Validate modality type exists
    modality_type = (
        db.query(ModalityType)
        .filter(ModalityType.id == modality_data.modality_type_id)
        .first()
    )
    if not modality_type:
        raise HTTPException(status_code=404, detail="Modality type not found")

    try:
        modality = Modality(
            name=modality_data.name,
            modality_type_id=modality_data.modality_type_id,
            created_by=DEFAULT_USER_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(modality)
        db.commit()
        db.refresh(modality)
        logger.info(f"Created modality: {modality.id}")
        return modality.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Modality with this name already exists"
        )


@router.get("/modalities/{modality_id}", response_model=ModalityResponse)
def get_modality(modality_id: UUID, db: Session = Depends(get_db_session)):
    """Get a modality by ID"""
    modality = db.query(Modality).filter(Modality.id == modality_id).first()
    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")
    return modality.to_dict()


@router.put("/modalities/{modality_id}", response_model=ModalityResponse)
def update_modality(
    modality_id: UUID,
    modality_data: ModalityUpdate,
    db: Session = Depends(get_db_session),
):
    """Update a modality"""
    modality = db.query(Modality).filter(Modality.id == modality_id).first()
    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    if modality_data.name is not None:
        modality.name = modality_data.name
    if modality_data.modality_type_id is not None:
        modality_type = (
            db.query(ModalityType)
            .filter(ModalityType.id == modality_data.modality_type_id)
            .first()
        )
        if not modality_type:
            raise HTTPException(status_code=404, detail="Modality type not found")
        modality.modality_type_id = modality_data.modality_type_id
    modality.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(modality)
        logger.info(f"Updated modality: {modality.id}")
        return modality.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Modality with this name already exists"
        )


@router.delete("/modalities/{modality_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_modality(modality_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a modality"""
    modality = db.query(Modality).filter(Modality.id == modality_id).first()
    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    db.delete(modality)
    db.commit()
    logger.info(f"Deleted modality: {modality_id}")


# ==================== STUDENT ENDPOINTS ====================
@router.get("/students", response_model=List[StudentResponse])
def list_students(db: Session = Depends(get_db_session)):
    """List all students"""
    students = db.query(Student).all()
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
        emit_event(
            db=db,
            event_type=EventTypes.STUDENT_CREATED,
            aggregate_type="student",
            aggregate_id=student.id,
            data=student.to_dict(),
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

    if student_data.full_name is not None:
        student.full_name = student_data.full_name
    if student_data.course_id is not None:
        course = db.query(Course).filter(Course.id == student_data.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        student.course_id = student_data.course_id
    if student_data.student_number is not None:
        student.student_number = student_data.student_number
    if student_data.is_member is not None:
        student.is_member = student_data.is_member
    student.updated_at = datetime.now(timezone.utc)

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

    db.delete(student)
    db.commit()
    logger.info(f"Deleted student: {student_id}")


# ==================== STAFF ENDPOINTS ====================
@router.get("/staff", response_model=List[StaffResponse])
def list_staff(db: Session = Depends(get_db_session)):
    """List all staff members"""
    staff = db.query(Staff).all()
    return [s.to_dict() for s in staff]


@router.post(
    "/staff", response_model=StaffResponse, status_code=status.HTTP_201_CREATED
)
def create_staff(staff_data: StaffCreate, db: Session = Depends(get_db_session)):
    """Create a new staff member"""
    # Validate that at least one of staff_number or contact is provided
    if not staff_data.staff_number and not staff_data.contact:
        raise HTTPException(
            status_code=400,
            detail="At least one of staff_number or contact must be provided",
        )

    try:
        staff = Staff(
            full_name=staff_data.full_name,
            staff_number=staff_data.staff_number,
            contact=staff_data.contact,
            created_by=DEFAULT_USER_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)
        logger.info(f"Created staff: {staff.id}")
        return staff.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Staff with this staff number or contact already exists",
        )


@router.get("/staff/{staff_id}", response_model=StaffResponse)
def get_staff(staff_id: UUID, db: Session = Depends(get_db_session)):
    """Get a staff member by ID"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return staff.to_dict()


@router.put("/staff/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: UUID, staff_data: StaffUpdate, db: Session = Depends(get_db_session)
):
    """Update a staff member"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    if staff_data.full_name is not None:
        staff.full_name = staff_data.full_name
    if staff_data.staff_number is not None:
        staff.staff_number = staff_data.staff_number
    if staff_data.contact is not None:
        staff.contact = staff_data.contact
    staff.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(staff)
        logger.info(f"Updated staff: {staff.id}")
        return staff.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Staff with this staff number or contact already exists",
        )


@router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(staff_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a staff member"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    db.delete(staff)
    db.commit()
    logger.info(f"Deleted staff: {staff_id}")


# ==================== TEAM ENDPOINTS ====================
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
        event_type=EventTypes.TEAM_CREATED,
        aggregate_type="team",
        aggregate_id=team.id,
        data=team.to_dict(),
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
                    event_type=EventTypes.TEAM_PLAYER_ADDED,
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
                    event_type=EventTypes.TEAM_PLAYER_REMOVED,
                    aggregate_type="team",
                    aggregate_id=team.id,
                    data={"team_id": str(team.id), "student_id": str(player_id)},
                )

    team.updated_at = datetime.now(timezone.utc)

    # Emit team updated event
    emit_event(
        db=db,
        event_type=EventTypes.TEAM_UPDATED,
        aggregate_type="team",
        aggregate_id=team.id,
        data=team.to_dict(include_players=True),
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

    db.delete(team)
    db.commit()
    logger.info(f"Deleted team: {team_id}")


@router.post("/teams/batch-get", response_model=List[TeamResponse])
def get_teams_by_ids(team_ids: List[UUID], db: Session = Depends(get_db_session)):
    """Get multiple teams by their IDs"""
    teams = db.query(Team).filter(Team.id.in_(team_ids)).all()
    return [team.to_dict(include_players=True) for team in teams]
