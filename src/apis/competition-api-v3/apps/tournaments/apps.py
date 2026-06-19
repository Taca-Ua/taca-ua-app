from django.apps import AppConfig


class TournamentsConfig(AppConfig):
    name = "apps.tournaments"

    def ready(self):
        # Import signals to ensure they are registered
        pass
