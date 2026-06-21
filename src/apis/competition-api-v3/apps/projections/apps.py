from django.apps import AppConfig


class ProjectionsConfig(AppConfig):
    name = "apps.projections"

    def ready(self):
        # Import signal handlers to ensure they are registered
        from . import signals  # noqa: F401
