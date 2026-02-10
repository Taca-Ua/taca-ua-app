"""
Match management serializers
"""

from rest_framework import serializers

from .students import StudentListSerializer
from .teams import TeamListSerializer

# ============= Participant Serializers =============


class ParticipantDetailSerializer(serializers.Serializer):
    """Serializer for participant details in match responses"""

    id = serializers.UUIDField()
    participant_type = serializers.CharField()
    team = TeamListSerializer(required=False, allow_null=True)
    athlete = StudentListSerializer(required=False, allow_null=True)
    score = serializers.IntegerField(required=False, allow_null=True)
    position = serializers.IntegerField(required=False, allow_null=True)


class ParticipantCreateSerializer(serializers.Serializer):
    """Serializer for adding a participant to a match"""

    participant_type = serializers.ChoiceField(
        choices=["team", "athlete"], required=True
    )
    team_id = serializers.UUIDField(required=False, allow_null=True)
    athlete_id = serializers.UUIDField(required=False, allow_null=True)

    def validate(self, data):
        if data["participant_type"] == "team" and not data.get("team_id"):
            raise serializers.ValidationError(
                "team_id is required when participant_type is 'team'."
            )
        if data["participant_type"] == "athlete" and not data.get("athlete_id"):
            raise serializers.ValidationError(
                "athlete_id is required when participant_type is 'athlete'."
            )
        return data


# ============= Match Serializers =============


class MatchListSerializer(serializers.Serializer):
    """Serializer for listing matches"""

    id = serializers.UUIDField()
    tournament_id = serializers.UUIDField(required=False, allow_null=True)
    location = serializers.CharField()
    start_time = serializers.DateTimeField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    participants = ParticipantDetailSerializer(many=True)


class MatchDetailSerializer(serializers.Serializer):
    """Serializer for detailed match view"""

    id = serializers.UUIDField()
    tournament_id = serializers.UUIDField(required=False, allow_null=True)
    location = serializers.CharField()
    start_time = serializers.DateTimeField()
    status = serializers.CharField()
    created_by = serializers.UUIDField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    participants = ParticipantDetailSerializer(many=True)


class MatchCreateSerializer(serializers.Serializer):
    """Serializer for creating a new match"""

    tournament_id = serializers.UUIDField(required=False, allow_null=True)
    location = serializers.CharField(required=True, max_length=255)
    start_time = serializers.DateTimeField(required=True)
    participants = ParticipantCreateSerializer(many=True, required=False)

    def validate_participants(self, value):
        if value and len(value) < 2:
            raise serializers.ValidationError(
                "A match must have at least 2 participants."
            )
        return value


class MatchUpdateSerializer(serializers.Serializer):
    """Serializer for updating match metadata"""

    location = serializers.CharField(required=False, max_length=255)
    start_time = serializers.DateTimeField(required=False)
    status = serializers.ChoiceField(
        choices=["scheduled", "in_progress", "finished", "cancelled"], required=False
    )


# ============= Result Serializers =============


class ParticipantResultSerializer(serializers.Serializer):
    """Serializer for individual participant result"""

    participant_id = serializers.UUIDField(required=True)
    score = serializers.IntegerField(required=False, allow_null=True)
    position = serializers.IntegerField(required=False, allow_null=True)
    result_metadata = serializers.JSONField(required=False, allow_null=True)


class MatchResultsUpdateSerializer(serializers.Serializer):
    """Serializer for updating match results"""

    participant_results = ParticipantResultSerializer(many=True, required=True)
    status = serializers.ChoiceField(
        choices=["scheduled", "in_progress", "finished", "cancelled"],
        required=False,
        default="finished",
    )

    def validate_participant_results(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one participant result is required."
            )
        return value


# ============= Lineup Serializers =============


class PlayerLineupSerializer(serializers.Serializer):
    """Serializer for individual player in lineup"""

    player_id = serializers.UUIDField(required=True)
    jersey_number = serializers.IntegerField(required=True, min_value=1, max_value=99)
    is_starter = serializers.BooleanField(required=False, default=True)


class LineupAssignSerializer(serializers.Serializer):
    """Serializer for assigning lineup to a team"""

    team_id = serializers.UUIDField(required=True)
    players = PlayerLineupSerializer(many=True, required=True)

    def validate_players(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one player is required in the lineup."
            )
        # Check for duplicate player IDs
        player_ids = [p["player_id"] for p in value]
        if len(player_ids) != len(set(player_ids)):
            raise serializers.ValidationError("Duplicate player IDs found in lineup.")
        # Check for duplicate jersey numbers
        jersey_numbers = [p["jersey_number"] for p in value]
        if len(jersey_numbers) != len(set(jersey_numbers)):
            raise serializers.ValidationError(
                "Duplicate jersey numbers found in lineup."
            )
        return value


class LineupDetailSerializer(serializers.Serializer):
    """Serializer for lineup details"""

    id = serializers.UUIDField()
    match_id = serializers.UUIDField()
    team_id = serializers.UUIDField()
    player_id = serializers.UUIDField()
    player = StudentListSerializer(required=False, allow_null=True)
    jersey_number = serializers.IntegerField()
    is_starter = serializers.BooleanField()
    created_at = serializers.DateTimeField()


# ============= Comment Serializers =============


class CommentCreateSerializer(serializers.Serializer):
    """Serializer for creating a comment"""

    message = serializers.CharField(required=True, max_length=1000)


class CommentDetailSerializer(serializers.Serializer):
    """Serializer for comment details"""

    id = serializers.UUIDField()
    match_id = serializers.UUIDField()
    message = serializers.CharField()
    created_by = serializers.UUIDField()
    created_at = serializers.DateTimeField()
