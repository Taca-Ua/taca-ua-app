import logging

from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthView(APIView):
    def get(self, request):
        logger.info("Health check endpoint called.")
        return Response({"status": "ok"})
