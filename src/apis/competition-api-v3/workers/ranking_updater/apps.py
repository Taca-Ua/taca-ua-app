from django.apps import AppConfig


class RankingUpdaterConfig(AppConfig):
    name = "workers.ranking_updater"

    def ready(self):
        from django.conf import settings

        # Update the application tag for Loki logging to include the ranking updater
        settings.LOGGING["handlers"]["loki"]["tags"][
            "application"
        ] += "-ranking-updater"
