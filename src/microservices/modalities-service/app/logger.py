import logging

import logging_loki

handler = logging_loki.LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"application": "modalities-service", "job": "modalities-service"},
    version="1",
)
logger = logging.getLogger("modalities-service")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
