"""
Tournament management serializers
"""

from rest_framework import serializers

from .modalities import ModalityListSerializer
from .teams import TeamListSerializer

STATUS_CHOICES = [
    ("draft", "Draft"),
    ("active", "Active"),
    ("finished", "Finished"),
]


class TournamentListSerializer(serializers.Serializer):
    """Serializer for listing tournaments"""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    status = serializers.ChoiceField(choices=STATUS_CHOICES, read_only=True)


class TournamentDetailSerializer(TournamentListSerializer):
    """Serializer for tournament details"""

    modality = ModalityListSerializer(read_only=True)
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    teams = TeamListSerializer(many=True, read_only=True)
    matches = serializers.ListField(
        child=serializers.DictField(), read_only=True, default=[]
    )


class TournamentCreateSerializer(serializers.Serializer):
    """Serializer for creating a tournament"""

    name = serializers.CharField(required=True)
    modality_id = serializers.UUIDField(required=True)
    team_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    start_date = serializers.DateTimeField(required=False, allow_null=True)


class TournamentUpdateSerializer(serializers.Serializer):
    """Serializer for updating a tournament"""

    name = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False)
    teams_add = serializers.ListField(child=serializers.UUIDField(), required=False)
    teams_remove = serializers.ListField(child=serializers.UUIDField(), required=False)


class TournamentFinishSerializer(serializers.Serializer):
    """Serializer for finishing a tournament"""

    class TournamentFinishEntrySerializer(serializers.Serializer):
        """Serializer for finishing a tournament entry"""

        team_id = serializers.UUIDField(required=True)
        position = serializers.IntegerField(required=True)

    ranking_entries = TournamentFinishEntrySerializer(many=True)
