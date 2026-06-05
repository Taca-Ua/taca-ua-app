from ..base import BaseFormat
from .models import DrawRule, LeagueSettings


class LeagueFormat(BaseFormat):

    def create(self, format_data: dict):
        LeagueSettings.objects.create(
            tournament=self.tournament,
            win_points=format_data.get("win_points", 3),
            draw_points=format_data.get("draw_points", 1),
            loss_points=format_data.get("loss_points", 0),
            draw_rule=format_data.get("draw_rule"),
        )

        return self.get_details()

    def update(self, format_data: dict):
        settings = LeagueSettings.objects.get(tournament=self.tournament)
        if not settings:
            raise ValueError("League settings not found for this tournament.")

        print(f"Updating league format with data: {format_data}")

        settings.win_points = format_data.get("win_points", settings.win_points)
        settings.draw_points = format_data.get("draw_points", settings.draw_points)
        settings.loss_points = format_data.get("loss_points", settings.loss_points)

        if (
            "draw_rule" in format_data
            and (format_data["draw_rule"] in DrawRule.values)
            or format_data["draw_rule"] is None
        ):
            settings.draw_rule = format_data.get("draw_rule", settings.draw_rule)
        else:
            raise ValueError(
                f"Invalid draw rule: {format_data['draw_rule']}. Must be one of {DrawRule.values} or None."
            )

        settings.save()

        return self.get_details()

    def get_details(self) -> dict:
        settings = LeagueSettings.objects.get(tournament=self.tournament)
        if not settings:
            raise ValueError("League settings not found for this tournament.")

        return {
            "win_points": settings.win_points,
            "draw_points": settings.draw_points,
            "loss_points": settings.loss_points,
            "draw_rule": settings.draw_rule,
        }
