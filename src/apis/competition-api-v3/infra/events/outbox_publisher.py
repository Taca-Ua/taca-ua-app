import logging

from django.db import transaction
from django.utils import timezone
from taca_events import EventType

from .models import OutboxEvent
from .rabbitmq import RabbitMQClient

logger = logging.getLogger(__name__)

BATCH_SIZE = 100


def publish_pending_events(rabbitmq_client: RabbitMQClient):
    with transaction.atomic():
        events = (
            OutboxEvent.objects.select_for_update(skip_locked=True)
            .filter(published=False)
            .order_by("id")[:BATCH_SIZE]
        )

        events = list(events)

    for event in events:
        try:
            rabbitmq_client.publish(
                routing_key=EventType.get_routing_key(event.event_type),
                body=event.payload,
            )

            event.published = True
            event.published_at = timezone.now()
            event.last_error = ""

            event.save(
                update_fields=[
                    "published",
                    "published_at",
                    "last_error",
                ]
            )
            logger.info(
                "Successfully published event %s (id=%s)",
                event.event_type,
                event.id,
            )

        except Exception as exc:
            logger.exception(
                "Failed publishing event %s (id=%s)",
                event.event_type,
                event.id,
            )

            event.last_error = str(exc)
            event.save(update_fields=["last_error"])
