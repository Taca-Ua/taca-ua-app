import logging

from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthView(APIView):
    schema = None  # Exclude from API schema

    def get(self, request):
        return Response({"status": "ok"})
