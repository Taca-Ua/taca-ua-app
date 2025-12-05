"""
Event handling for Modalities Service.
"""

import logging
from typing import Any, Dict
from uuid import UUID

from taca_messaging import RabbitMQService

logger = logging.getLogger("modalities-service")

rabbitmq_service = RabbitMQService(service_name="modalities-service")


class FakeObject:
    """Temporary placeholder for Modality object when None is provided."""

    def __init__(self, _id):
        self.id = _id


# Event Publishers
async def publish_modality_created(modality):
    """Publish ModalityCreated event."""
    if not rabbitmq_service:
        return

    if modality is None:
        modality = FakeObject(_id="unknown")

    event_data = {}

    await rabbitmq_service.publish_event("modality.created", event_data)
    logger.info(f"Published modality.created event for modality {modality.id}")


async def publish_modality_updated(modality, changes: Dict[str, Any]):
    """Publish ModalityUpdated event."""
    if not rabbitmq_service:
        return

    if modality is None:
        modality = FakeObject(_id="unknown")

    event_data = {}

    await rabbitmq_service.publish_event("modality.updated", event_data)
    logger.info(f"Published modality.updated event for modality {modality.id}")


async def publish_modality_deleted(modality_id: UUID):
    """Publish ModalityDeleted event."""
    if not rabbitmq_service:
        return

    event_data = {}

    await rabbitmq_service.publish_event("modality.deleted", event_data)
    logger.info(f"Published modality.deleted event for modality {modality_id}")


async def publish_team_created(team):
    """Publish TeamCreated event."""
    if not rabbitmq_service:
        return

    if team is None:
        team = FakeObject(_id="unknown")

    event_data = {}

    await rabbitmq_service.publish_event("team.created", event_data)
    logger.info(f"Published team.created event for team {team.id}")


async def publish_team_updated(team, changes: Dict[str, Any]):
    """Publish TeamUpdated event."""
    if not rabbitmq_service:
        return

    if team is None:
        team = FakeObject(_id="unknown")

    event_data = {}

    await rabbitmq_service.publish_event("team.updated", event_data)
    logger.info(f"Published team.updated event for team {team.id}")


async def publish_team_deleted(team_id: UUID):
    """Publish TeamDeleted event."""
    if not rabbitmq_service:
        return

    if team_id is None:
        team_id = "unknown"

    event_data = {}

    await rabbitmq_service.publish_event("team.deleted", event_data)
    logger.info(f"Published team.deleted event for team {team_id}")


async def publish_student_created(student):
    """Publish StudentCreated event."""
    if not rabbitmq_service:
        return

    if student is None:
        student = FakeObject(_id="unknown")

    event_data = {}

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
