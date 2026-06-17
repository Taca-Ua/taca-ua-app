import logging

from apps.ranking.service import recompute_rankings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        recompute_rankings()
