"""
Tournament management serializers
"""

from rest_framework import serializers


class TournamentListSerializer(serializers.Serializer):
    """Serializer for listing tournaments"""

    id = serializers.UUIDField(read_only=True)
    modality_id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    status = serializers.ChoiceField(
        choices=["draft", "active", "finished"], read_only=True
    )
    start_date = serializers.DateTimeField(required=False, allow_null=True)


class TournamentDetailSerializer(TournamentListSerializer):
    """Serializer for tournament details"""

    created_by = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)
    finished_at = serializers.DateTimeField(read_only=True, allow_null=True)
    finished_by = serializers.UUIDField(read_only=True, allow_null=True)
    ranking_positions = serializers.ListField(required=False, read_only=True)


class TournamentCreateSerializer(serializers.Serializer):
    """Serializer for creating a tournament"""

    modality_id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True)
    team_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    start_date = serializers.DateTimeField(required=False, allow_null=True)


class TournamentUpdateSerializer(serializers.Serializer):
    """Serializer for updating a tournament"""

    name = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    status = serializers.ChoiceField(
        choices=["draft", "active", "finished"], required=False
    )
    teams_add = serializers.ListField(child=serializers.UUIDField(), required=False)
    teams_remove = serializers.ListField(child=serializers.UUIDField(), required=False)


class TournamentFinishSerializer(serializers.Serializer):
    """Serializer for finishing a tournament"""

    class TournamentFinishEntrySerializer(serializers.Serializer):
        """Serializer for finishing a tournament entry"""

        team_id = serializers.UUIDField(required=True)
        position = serializers.IntegerField(required=True)

    ranking_entries = TournamentFinishEntrySerializer(many=True)
