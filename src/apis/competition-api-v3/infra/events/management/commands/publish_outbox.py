import logging
import time

from django.core.management.base import BaseCommand
from infra.events.outbox_publisher import publish_pending_events
from infra.events.rabbitmq import RabbitMQClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        rabbitmq_client = RabbitMQClient()
        logger.info("Starting outbox publisher loop...")
        while True:
            try:
                publish_pending_events(rabbitmq_client)

            except Exception:
                logger.exception("Outbox publisher loop failed")

            time.sleep(5)
