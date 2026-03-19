from rest_framework import serializers

from ..matches.serializers import MatchListSerializer
from ..modalities.serializers import ModalityListSerializer

# Helpers
STATUS_CHOICES = (
    ("scheduled", "Scheduled"),
    ("ongoing", "Ongoing"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
)


class CompetitorSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    course_name = serializers.CharField(max_length=255)


# Main Serializers
class TournamentListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    modality = ModalityListSerializer()
    status = serializers.ChoiceField(choices=STATUS_CHOICES)


class TournamentDetailSerializer(TournamentListSerializer):
    competitors = CompetitorSerializer(many=True)
    matches = MatchListSerializer(many=True)
    standings = ...


class TournamentCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    modality_id = serializers.UUIDField()


class TournamentUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    modality_id = serializers.UUIDField(required=False)
