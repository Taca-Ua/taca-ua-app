from django.apps import AppConfig


class RankingConfig(AppConfig):
    name = "apps.ranking"

    def ready(self):
        from . import signals  # noqa: F401
