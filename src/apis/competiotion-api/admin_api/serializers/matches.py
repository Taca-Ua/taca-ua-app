"""
Match management serializers
"""

from rest_framework import serializers


class MatchListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    team_home_name = serializers.CharField()
    team_away_name = serializers.CharField()
    team_home_id = serializers.UUIDField(required=False)
    team_away_id = serializers.UUIDField(required=False)
    location = serializers.CharField()
    start_time = serializers.DateTimeField()
    status = serializers.CharField()

    home_score = serializers.IntegerField(required=False)
    away_score = serializers.IntegerField(required=False)


class MatchCreateSerializer(serializers.Serializer):
    tournament_id = serializers.UUIDField()
    team_home_id = serializers.UUIDField()
    team_away_id = serializers.UUIDField()
    location = serializers.CharField()
    start_time = serializers.DateTimeField()


class MatchUpdateSerializer(serializers.Serializer):
    location = serializers.CharField(required=False)
    start_time = serializers.DateTimeField(required=False)
    status = serializers.CharField(required=False)
    home_score = serializers.IntegerField(required=False)
    away_score = serializers.IntegerField(required=False)


class MatchResultSerializer(serializers.Serializer):
    """Serializer for registering match result"""

    home_score = serializers.IntegerField(required=True)
    away_score = serializers.IntegerField(required=True)


class MatchLineupSerializer(serializers.Serializer):
    """Serializer for assigning players to match"""

    class PlayerLineupSerializer(serializers.Serializer):
        player_id = serializers.UUIDField(required=True)
        jersey_number = serializers.IntegerField(required=True)
        is_starter = serializers.BooleanField(required=True)

    team_id = serializers.UUIDField(required=True)
    players = serializers.ListField(
        child=PlayerLineupSerializer(), required=True, help_text="List of player IDs"
    )


class MatchCommentSerializer(serializers.Serializer):
    """Serializer for adding match comments"""

    message = serializers.CharField(required=True)
