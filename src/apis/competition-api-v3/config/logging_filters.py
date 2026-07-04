import logging


class IgnoreHealthMetricsFilter(logging.Filter):
    EXCLUDED_PATHS = {"/metrics", "/api/admin/health/"}

    def filter(self, record):
        try:
            msg = record.getMessage()
            path = msg.split()[1] if msg else ""
        except Exception:
            return True

        return path not in self.EXCLUDED_PATHS


class IgnoreHealthMetricsAccessFilter(logging.Filter):
    EXCLUDED_PATHS = {"/metrics", "/api/admin/health/"}

    def filter(self, record):
        try:
            path = record.args["U"]
            return path not in self.EXCLUDED_PATHS
        except Exception:
            return True
