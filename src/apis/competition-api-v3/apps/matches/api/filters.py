from rest_framework import serializers

from ..models import MatchStatus


class MatchListFilterSerializer(serializers.Serializer):
    """Serializer for match list filters"""

    tournament_id = serializers.UUIDField(required=False)
    modality_id = serializers.UUIDField(required=False)
    course_id = serializers.UUIDField(required=False)
    nucleus_id = serializers.UUIDField(required=False)
    team_id = serializers.UUIDField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    status = serializers.ChoiceField(choices=MatchStatus.values, required=False)

    page = serializers.IntegerField(required=False)
    limit = serializers.IntegerField(required=False)

    def validate(self, data: dict) -> dict:
        # Validate date range
        if (
            data.get("date_from")
            and data.get("date_to")
            and data["date_from"] > data["date_to"]
        ):
            raise serializers.ValidationError("date_from must be before date_to.")

        # Validate pagination parameters
        if (data.get("page") is None) != (data.get("limit") is None):
            raise serializers.ValidationError(
                "Both page and limit must be provided together."
            )

        return data
