from django.apps import AppConfig


class AppsConfig(AppConfig):
    name = "apps"

    def ready(self):
        # Import signal handlers to ensure they are registered
        import apps.tournaments.formats.league.signals  # noqa: F401

        pass
