"""
Tournament management serializers
"""

from rest_framework import serializers


class TournamentListSerializer(serializers.Serializer):
    """Serializer for listing tournaments"""

    id = serializers.IntegerField(read_only=True)
    modality_id = serializers.IntegerField()
    name = serializers.CharField()
    season_id = serializers.IntegerField()
    season_year = serializers.CharField(required=False)
    rules = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=["draft", "active", "finished"], read_only=True
    )
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    teams = serializers.ListField(child=serializers.IntegerField(), required=False)


class TournamentCreateSerializer(serializers.Serializer):
    """Serializer for creating a tournament"""

    modality_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    season_id = serializers.IntegerField(required=True)
    season_year = serializers.CharField(required=False)
    rules = serializers.CharField(required=False, allow_blank=True)
    teams = serializers.ListField(child=serializers.IntegerField(), required=False)
    start_date = serializers.DateTimeField(required=False, allow_null=True)


class TournamentUpdateSerializer(serializers.Serializer):
    """Serializer for updating a tournament"""

    name = serializers.CharField(required=False)
    rules = serializers.CharField(required=False, allow_blank=True)
    teams = serializers.ListField(child=serializers.IntegerField(), required=False)
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    status = serializers.ChoiceField(
        choices=["draft", "active", "finished"], required=False
    )
