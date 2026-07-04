import logging
import time

from apps.matches.models import Match
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


@transaction.atomic
def update_scheduled_matches():
    matches = Match.objects.filter(
        status=Match.Status.SCHEDULED, scheduled_time__lte=timezone.now()
    )

    c = 0
    for match in matches:
        match.status = Match.Status.IN_PROGRESS
        match.save()
        c += 1

    logger.info(f"Updated [{c}] matches from SCHEDULED to IN_PROGRESS.")


@transaction.atomic
def update_ongoing_matches():
    matches = Match.objects.filter(
        status=Match.Status.IN_PROGRESS, scheduled_time__lte=timezone.now().date()
    )

    c = 0
    for match in matches:
        match.status = Match.Status.FINISHED
        match.save()
        c += 1

    logger.info(f"Updated [{c}] matches from IN_PROGRESS to FINISHED")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        logger.info("Starting matches state updater worker...")
        while True:
            try:
                update_scheduled_matches()
                update_ongoing_matches()

                time.sleep(60)  # Sleep for 1 minute before checking again
            except Exception as e:
                logger.error(f"Error fetching matches: {e}")
                time.sleep(60)
                continue
