import logging

from apps.seasons.service import create_initial_season
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        logger.info("Bootstrapping season...")
        create_initial_season(settings.DEFAULT_SEASON_NAME)
        logger.info("Season bootstrapped successfully.")
