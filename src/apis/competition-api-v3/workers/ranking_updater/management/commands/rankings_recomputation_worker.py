import logging
import time

from django.core.management.base import BaseCommand

from ...service import handle_pending_recomputation_requests

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        logger.info("Starting rankings recomputation worker...")
        while True:
            handle_pending_recomputation_requests()
            time.sleep(10)  # Sleep for a short period before checking for new requests
