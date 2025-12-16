"""
Event handling for Modalities Service.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID

from taca_messaging import RabbitMQService

from .logger import logger
from .models import Course, Modality, Student, Team

rabbitmq_service = RabbitMQService(service_name="modalities-service")


# Event Publishers
async def publish_course_created(course: Course):
    """Publish CourseCreated event."""
    if not rabbitmq_service:
        return

    event_data = {
        "course_id": str(course.id),
        "name": course.name,
        "abbreviation": course.abbreviation,
        "description": course.description,
        "logo_url": course.logo_url,
        "created_at": course.created_at.isoformat(),
    }

    await rabbitmq_service.publish_event("course.created", event_data)
    logger.info(f"Published course.created event for course {course.id}")


async def publish_course_updated(course: Course, changes: Dict[str, Any]):
    """Publish CourseUpdated event."""
    if not rabbitmq_service:
        return

    event_data = {
        "course_id": str(course.id),
        "changes": changes,
        "updated_at": course.updated_at.isoformat() if course.updated_at else None,
    }

    await rabbitmq_service.publish_event("course.updated", event_data)
    logger.info(f"Published course.updated event for course {course.id}")


async def publish_course_deleted(course_id: UUID):
    """Publish CourseDeleted event."""
    if not rabbitmq_service:
        return

    event_data = {
        "course_id": str(course_id),
        "deleted_at": datetime.now(timezone.utc).isoformat(),
    }

    await rabbitmq_service.publish_event("course.deleted", event_data)
    logger.info(f"Published course.deleted event for course {course_id}")


async def publish_modality_created(modality: Modality):
    """Publish ModalityCreated event."""
    if not rabbitmq_service:
        return

    event_data = {
        "modality_id": str(modality.id),
        "name": modality.name,
        "type": modality.type.value,
        "created_at": modality.created_at.isoformat(),
    }

    await rabbitmq_service.publish_event("modality.created", event_data)
    logger.info(f"Published modality.created event for modality {modality.id}")


async def publish_modality_updated(modality: Modality, changes: Dict[str, Any]):
    """Publish ModalityUpdated event."""
    if not rabbitmq_service:
        return

    event_data = {
        "modality_id": str(modality.id),
        "changes": changes,
        "updated_at": modality.updated_at.isoformat() if modality.updated_at else None,
    }

    await rabbitmq_service.publish_event("modality.updated", event_data)
    logger.info(f"Published modality.updated event for modality {modality.id}")


async def publish_modality_deleted(modality_id: UUID):
    """Publish ModalityDeleted event."""
    if not rabbitmq_service:
        return

    event_data = {
        "modality_id": str(modality_id),
        "deleted_at": datetime.now(timezone.utc).isoformat(),
    }

    await rabbitmq_service.publish_event("modality.deleted", event_data)
    logger.info(f"Published modality.deleted event for modality {modality_id}")


async def publish_team_created(team: Team):
    """Publish TeamCreated event."""
    if not rabbitmq_service:
        return

    event_data = {
        "team_id": str(team.id),
        "modality_id": str(team.modality_id),
        "course_id": str(team.course_id),
        "name": team.name,
        "players": [str(p) for p in (team.players or [])],
        "created_at": team.created_at.isoformat(),
    }

    await rabbitmq_service.publish_event("team.created", event_data)
    logger.info(f"Published team.created event for team {team.id}")


async def publish_team_updated(team: Team, changes: Dict[str, Any]):
    """Publish TeamUpdated event."""
    if not rabbitmq_service:
        return

    event_data = {
        "team_id": str(team.id),
        "changes": changes,
        "updated_at": team.updated_at.isoformat() if team.updated_at else None,
    }

    await rabbitmq_service.publish_event("team.updated", event_data)
    logger.info(f"Published team.updated event for team {team.id}")


async def publish_team_deleted(team_id: UUID):
    """Publish TeamDeleted event."""
    if not rabbitmq_service:
        return

    event_data = {
        "team_id": str(team_id),
        "deleted_at": datetime.now(timezone.utc).isoformat(),
    }

    await rabbitmq_service.publish_event("team.deleted", event_data)
    logger.info(f"Published team.deleted event for team {team_id}")


async def publish_student_created(student: Student):
    """Publish StudentCreated event."""
    if not rabbitmq_service:
        return

    event_data = {
        "student_id": str(student.id),
        "course_id": str(student.course_id),
        "full_name": student.full_name,
        "student_number": student.student_number,
        "created_at": student.created_at.isoformat(),
    }

    await rabbitmq_service.publish_event("student.created", event_data)
    logger.info(f"Published student.created event for student {student.id}")


@rabbitmq_service.event_handler("course.deleted")
async def handle_course_deleted(data: dict):
    """
    Consumes: course.deleted

    Remove all teams and students from this course.
    """
    course_id = data.get("course_id")
    logger.info(f"Handling course.deleted event for course {course_id}")

    # Implementation to be added when database operations are needed
    # - Find all teams with this course_id
    # - Delete them and publish team.deleted events
    # - Find all students with this course_id
    # - Delete them
    logger.warning("CourseDeleted handler not fully implemented yet")
