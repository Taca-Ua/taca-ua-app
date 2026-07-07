import json
import logging
import time

from shared.auth.utils import get_user

logger = logging.getLogger("request_logger")


class RequestLoggingMiddleware:
    EXCLUDED_PATHS = {"/metrics", "/api/admin/health/"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()

        body = None
        try:
            body = request.body
        except Exception:
            pass

        response = self.get_response(request)
        user = get_user(request)

        duration_ms = round((time.time() - start) * 1000)

        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body = json.loads(body)
            except Exception:
                body = None

        if request.path in self.EXCLUDED_PATHS:
            return response

        logger_func = logger.info
        if response.status_code >= 500:
            logger_func = logger.error
        elif response.status_code >= 400:
            logger_func = logger.warning

        logger_func(
            "http_request",
            extra={
                "method": request.method,
                "path": request.path,
                "query": json.dumps(request.GET.dict()),
                "payload": json.dumps(body) if body else None,
                "response": (
                    json.dumps(response.data) if hasattr(response, "data") else None
                ),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "user": user.user_id if user else None,
            },
        )

        return response
