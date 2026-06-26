import logging

from django.core.management.base import BaseCommand

from ...service import create_initial_config

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        logger.info("Bootstrapping homepage configuration...")
        create_initial_config()
        logger.info("Homepage configuration bootstrapped successfully.")
