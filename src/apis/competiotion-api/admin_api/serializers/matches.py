"""
Match management serializers
"""

from rest_framework import serializers

from .students import StudentListSerializer
from .teams import TeamListSerializer


class _ParticipantSerializer(serializers.Serializer):
    participant_type = serializers.CharField()
    team = TeamListSerializer(required=False)
    athlete = StudentListSerializer(required=False)

    def validate(self, data):
        if data["participant_type"] == "team" and "team" not in data:
            raise serializers.ValidationError(
                "Team data is required for team participants."
            )
        if data["participant_type"] == "athlete" and "athlete" not in data:
            raise serializers.ValidationError(
                "Athlete data is required for athlete participants."
            )
        return data


class MatchListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    participants = _ParticipantSerializer(many=True)
    location = serializers.CharField()
    start_time = serializers.DateTimeField()
    status = serializers.CharField()

    home_score = serializers.IntegerField(required=False)
    away_score = serializers.IntegerField(required=False)


class MatchDetailSerializer(MatchListSerializer):
    class _TeamLineupSerializer(TeamListSerializer):
        """Nested serializer for team lineup"""

        players = StudentListSerializer(many=True)

    team_home = _TeamLineupSerializer()
    team_away = _TeamLineupSerializer()
    additional_details = serializers.JSONField(required=False)


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


class MatchResultRequestSerializer(serializers.Serializer):
    """Serializer for registering match result"""

    home_score = serializers.IntegerField(required=True)
    away_score = serializers.IntegerField(required=True)


class MatchLineupRequestSerializer(serializers.Serializer):
    """Serializer for assigning players to match"""

    class PlayerLineupSerializer(serializers.Serializer):
        player_id = serializers.UUIDField(required=True)
        jersey_number = serializers.IntegerField(required=True)
        is_starter = serializers.BooleanField(required=True)

    team_id = serializers.UUIDField(required=True)
    players = serializers.ListField(
        child=PlayerLineupSerializer(), required=True, help_text="List of player IDs"
    )


class MatchCommentRequestSerializer(serializers.Serializer):
    """Serializer for adding match comments"""

    message = serializers.CharField(required=True)
