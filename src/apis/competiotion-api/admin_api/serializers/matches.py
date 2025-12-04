"""
Match management serializers
"""

from rest_framework import serializers


class MatchListSerializer(serializers.Serializer):
    """Serializer for listing matches"""

    id = serializers.IntegerField(read_only=True)
    tournament_id = serializers.IntegerField()
    team_home_id = serializers.IntegerField()
    team_away_id = serializers.IntegerField()
    location = serializers.CharField()
    start_time = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=["scheduled", "finished"], read_only=True)
    home_score = serializers.IntegerField(required=False, allow_null=True)
    away_score = serializers.IntegerField(required=False, allow_null=True)


class MatchCreateSerializer(serializers.Serializer):
    """Serializer for creating a match"""

    tournament_id = serializers.IntegerField(required=True)
    team_home_id = serializers.IntegerField(required=True)
    team_away_id = serializers.IntegerField(required=True)
    location = serializers.CharField(required=True)
    start_time = serializers.DateTimeField(required=True)


class MatchUpdateSerializer(serializers.Serializer):
    """Serializer for updating a match"""

    location = serializers.CharField(required=False)
    start_time = serializers.DateTimeField(required=False)
    team_home_id = serializers.IntegerField(required=False)
    team_away_id = serializers.IntegerField(required=False)


class MatchResultSerializer(serializers.Serializer):
    """Serializer for registering match result"""

    home_score = serializers.IntegerField(required=True)
    away_score = serializers.IntegerField(required=True)


class PlayerLineupSerializer(serializers.Serializer):
    """Serializer for player in lineup"""

    player_id = serializers.IntegerField(required=True)
    jersey_number = serializers.IntegerField(required=False)


class MatchLineupSerializer(serializers.Serializer):
    """Serializer for assigning players to match"""

    team_id = serializers.IntegerField(required=True)
    players = serializers.ListField(
        child=serializers.IntegerField(), required=True, help_text="List of player IDs"
    )


class MatchCommentSerializer(serializers.Serializer):
    """Serializer for adding match comments"""

    message = serializers.CharField(required=True)
