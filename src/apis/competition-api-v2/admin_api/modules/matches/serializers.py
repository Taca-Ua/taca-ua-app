"""
Match management serializers
"""

from rest_framework import serializers


# Helper serializers
class ParticipantsListSerializer(serializers.Serializer):
    """Serializer for listing match participants"""

    id = serializers.UUIDField()
    entity_id = serializers.UUIDField()
    name = serializers.CharField()
    score = serializers.IntegerField(required=False, allow_null=True)
    position = serializers.IntegerField(required=False, allow_null=True)


class CommentListSerializer(serializers.Serializer):
    """Serializer for listing comments on a match"""

    id = serializers.UUIDField()
    message = serializers.CharField()
    author_name = serializers.CharField()
    can_edit = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField()


class LineupDetailSerializer(serializers.Serializer):
    """Serializer for lineup details"""

    class PlayerLineupSerializer(serializers.Serializer):
        """Serializer for individual player in lineup"""

        player_id = serializers.UUIDField()
        player_name = serializers.CharField()
        player_course = serializers.CharField(required=False, allow_null=True)
        is_starter = serializers.BooleanField(required=False, default=None)
        jersey_number = serializers.IntegerField(required=False, allow_null=True)

    participant_id = serializers.UUIDField()
    lineup = PlayerLineupSerializer(many=True)


# Response serializers
class MatchListSerializer(serializers.Serializer):
    """Serializer for listing matches"""

    id = serializers.UUIDField()
    tournament_id = serializers.UUIDField(required=False, allow_null=True)
    location = serializers.CharField()
    start_time = serializers.DateTimeField()
    status = serializers.CharField()
    participants = ParticipantsListSerializer(many=True)


class MatchDetailSerializer(MatchListSerializer):
    """Serializer for detailed match view"""

    comments = CommentListSerializer(many=True, required=False, allow_null=True)
    lineups = LineupDetailSerializer(many=True, required=False, allow_null=True)


# Request serializers
class MatchListFilterSerializer(serializers.Serializer):
    """Serializer for match list filters"""

    tournament_id = serializers.UUIDField(required=False)
    status = serializers.ChoiceField(
        choices=["scheduled", "in_progress", "finished", "cancelled"],
        required=False,
    )


class MatchCreateSerializer(serializers.Serializer):
    """Serializer for creating a new match"""

    tournament_id = serializers.UUIDField(required=False, allow_null=True)
    location = serializers.CharField(required=True, max_length=255)
    start_time = serializers.DateTimeField(required=True)
    participants = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        allow_empty=False,
        help_text="List of tournament participants IDs participating in the match",
    )
    journey = serializers.IntegerField(required=False, allow_null=True)

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


class MatchPublishResultsSerializer(serializers.Serializer):
    """Serializer for publishing match results"""

    class ParticipantResultSerializer(serializers.Serializer):
        """Serializer for individual participant result"""

        participant_id = serializers.UUIDField(required=True)
        score = serializers.IntegerField(required=False, allow_null=True)
        position = serializers.IntegerField(required=False, allow_null=True)

        def validate(self, data):
            if data.get("score") is None and data.get("position") is None:
                raise serializers.ValidationError(
                    "At least one of score or position must be provided for each participant."
                )
            return data

    participant_results = ParticipantResultSerializer(many=True, required=True)
    status = serializers.ChoiceField(
        choices=["in_progress", "finished"],
        required=False,
        default="finished",
    )


class CommentCreateSerializer(serializers.Serializer):
    """Serializer for creating a comment"""

    message = serializers.CharField(required=True, max_length=1000)


class LineupAssignSerializer(serializers.Serializer):
    """Serializer for assigning lineup to a team"""

    participant = serializers.UUIDField(required=True)
    players = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        allow_empty=True,
        help_text="List of player IDs to assign to the lineup",
    )

    def validate_players(self, value):
        # Ensure all player IDs are unique
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Player IDs must be unique.")

        return value


class LineupUpdateSerializer(serializers.Serializer):
    """Serializer for updating lineup of a team"""

    class PlayerLineupUpdateSerializer(serializers.Serializer):
        """Serializer for individual player in lineup update"""

        player_id = serializers.UUIDField()
        is_starter = serializers.BooleanField(required=False, default=None)
        jersey_number = serializers.IntegerField(required=False, allow_null=True)

    participant = serializers.UUIDField(required=True)
    players = PlayerLineupUpdateSerializer(many=True, required=True)
