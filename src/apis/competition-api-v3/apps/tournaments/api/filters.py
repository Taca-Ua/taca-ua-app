from rest_framework import serializers

from ..models import TournamentStatus


class TournamentListQuerySerializer(serializers.Serializer):
    """Serializer for tournament list query parameters"""

    status = serializers.ChoiceField(choices=TournamentStatus.choices, required=False)
    modality_id = serializers.UUIDField(required=False)
    season_id = serializers.IntegerField(required=False)
    course_id = serializers.UUIDField(required=False)
