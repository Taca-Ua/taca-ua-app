"""
Tournament management serializers
"""

from rest_framework import serializers

from .matches import MatchListSerializer
from .modalities import ModalityListSerializer, ModalityTypeListSerializer
from .students import StudentListSerializer
from .teams import TeamListSerializer

STATUS_CHOICES = [
    ("draft", "Draft"),
    ("active", "Active"),
    ("finished", "Finished"),
]

COMPETITOR_TYPE_CHOICES = [
    ("team", "Team"),
    ("athlete", "Athlete"),
]


class TournamentCompetitorSerializer(serializers.Serializer):
    """
    A competitor subscribed to a tournament.
    """

    competitor_type = serializers.ChoiceField(choices=COMPETITOR_TYPE_CHOICES)
    team_id = serializers.CharField(required=False, allow_null=True)
    athlete_id = serializers.CharField(required=False, allow_null=True)

    def validate(self, data):
        if data["competitor_type"] == "team" and not data.get("team_id"):
            raise serializers.ValidationError("team_id is required for type 'team'")

        if data["competitor_type"] == "athlete" and not data.get("athlete_id"):
            raise serializers.ValidationError(
                "athlete_id is required for type 'athlete'"
            )

        return data


class TournamentCompetitorDetailSerializer(serializers.Serializer):
    """
    Detailed information about a competitor subscribed to a tournament.
    """

    id = serializers.UUIDField()
    competitor_type = serializers.ChoiceField(choices=COMPETITOR_TYPE_CHOICES)
    team = TeamListSerializer(required=False, allow_null=True)
    athlete = StudentListSerializer(required=False, allow_null=True)

    def validate(self, data):
        if data["competitor_type"] == "team" and not data.get("team"):
            raise serializers.ValidationError("team is required for type 'team'")

        if data["competitor_type"] == "athlete" and not data.get("athlete"):
            raise serializers.ValidationError("athlete is required for type 'athlete'")

        return data


class TournamentListSerializer(serializers.Serializer):
    """Serializer for listing tournaments"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    modality = ModalityListSerializer()
    start_date = serializers.DateTimeField(required=False, allow_null=True)


class TournamentDetailSerializer(TournamentListSerializer):
    """Serializer for tournament details"""

    start_date = serializers.DateTimeField(required=False, allow_null=True)
    scoring_format = ModalityTypeListSerializer()
    competitor_type = serializers.ChoiceField(choices=COMPETITOR_TYPE_CHOICES)

    competitors = TournamentCompetitorDetailSerializer(many=True)
    matches = MatchListSerializer(many=True)


class TournamentCreateSerializer(serializers.Serializer):
    """Serializer for creating a tournament"""

    name = serializers.CharField(required=True)
    modality_id = serializers.UUIDField(required=True)
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    is_playoff = serializers.BooleanField(required=False, default=False)


class TournamentUpdateSerializer(serializers.Serializer):
    """Serializer for updating a tournament"""

    name = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False)
    is_playoff = serializers.BooleanField(default=None, required=False)


class TournamentFinishSerializer(serializers.Serializer):
    """Serializer for finishing a tournament"""

    class TournamentFinishEntrySerializer(TournamentCompetitorSerializer):
        """Serializer for finishing a tournament entry"""

        position = serializers.IntegerField(required=True)
        competitor_id = serializers.UUIDField(required=True)

    ranking_entries = TournamentFinishEntrySerializer(many=True)


class TournamentCompetitorsDeleteSerializer(serializers.Serializer):
    """Serializer for deleting competitors from a tournament"""

    competitors_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )
