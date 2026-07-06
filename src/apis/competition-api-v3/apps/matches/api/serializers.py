from rest_framework import serializers


# Helper serializers
class MatchParticipantLineupSerializer(serializers.Serializer):
    """Serializer for lineup details"""

    class PlayerLineupSerializer(serializers.Serializer):
        """Serializer for individual player in lineup"""

        player_id = serializers.UUIDField()
        player_name = serializers.CharField()
        player_course = serializers.CharField(required=False, allow_null=True)
        is_starter = serializers.BooleanField(required=False, default=None)
        jersey_number = serializers.IntegerField(required=False, allow_null=True)

    class StaffAssignmentSerializer(serializers.Serializer):
        """Serializer for staff assigned to a match participant"""

        id = serializers.UUIDField()
        staff_id = serializers.UUIDField()
        name = serializers.CharField()

    id = serializers.UUIDField()
    name = serializers.CharField()
    team_id = serializers.UUIDField(required=False, allow_null=True, source="entity_id")
    lineup = PlayerLineupSerializer(many=True)
    staff = StaffAssignmentSerializer(many=True, required=False)


# Response serializers
class MatchListSerializer(serializers.Serializer):
    """Serializer for listing matches"""

    class ParticipantsListSerializer(serializers.Serializer):
        """Serializer for listing match participants"""

        id = serializers.UUIDField()
        name = serializers.CharField()
        score = serializers.IntegerField(required=False, allow_null=True)
        position = serializers.IntegerField(required=False, allow_null=True)
        logo_url = serializers.CharField(required=False, allow_null=True)
        can_edit = serializers.BooleanField(default=True)

    class TournamentSummarySerializer(serializers.Serializer):
        """Serializer for tournament summary information"""

        id = serializers.UUIDField()
        name = serializers.CharField()

    id = serializers.UUIDField()
    tournament = TournamentSummarySerializer()
    location = serializers.CharField()
    start_time = serializers.DateTimeField(source="scheduled_time")
    status = serializers.CharField()
    participants = ParticipantsListSerializer(many=True)

    format_specific_data = serializers.DictField(required=False, allow_null=True)


class MatchDetailSerializer(MatchListSerializer):
    """Serializer for detailed match view"""

    class CommentListSerializer(serializers.Serializer):
        """Serializer for listing comments on a match"""

        id = serializers.UUIDField()
        message = serializers.CharField(source="content")
        author_name = serializers.CharField(source="author")
        can_edit = serializers.BooleanField(default=True)
        created_at = serializers.DateTimeField(source="timestamp")

    comments = CommentListSerializer(many=True, required=False, allow_null=True)


class MatchPaginatedListSerializer(serializers.Serializer):
    """Serializer for paginated match list response"""

    matches = MatchListSerializer(many=True)
    total = serializers.IntegerField()


# Request serializers
class MatchCreateSerializer(serializers.Serializer):
    """Serializer for creating a new match"""

    tournament_id = serializers.UUIDField(required=False, allow_null=True)
    location = serializers.CharField(required=False, max_length=255, allow_null=True)
    start_time = serializers.DateTimeField(required=False, allow_null=True)
    participants = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        allow_empty=False,
        help_text="List of tournament participants IDs participating in the match",
    )

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

    def validate_participant_results(self, value):
        participant_ids = [pr["participant_id"] for pr in value]
        if len(participant_ids) != len(set(participant_ids)):
            raise serializers.ValidationError(
                "Participant IDs in results must be unique."
            )

        # all must be score or all must be position
        all_score = all(pr.get("score") is not None for pr in value)
        all_position = all(pr.get("position") is not None for pr in value)
        if not (all_score or all_position):
            raise serializers.ValidationError(
                "All participant results must include either score or position, but not a mix of both."
            )

        return value


class CommentCreateSerializer(serializers.Serializer):
    """Serializer for creating a comment"""

    message = serializers.CharField(required=True, max_length=1000)


class LineupAssignSerializer(serializers.Serializer):
    """Serializer for assigning lineup to a team"""

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

    players = PlayerLineupUpdateSerializer(many=True, required=True)


class LineupAssignStaffSerializer(serializers.Serializer):
    """Serializer for assigning staff to a match participant"""

    staff_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        allow_empty=True,
        help_text="List of staff IDs to assign to the match participant",
    )

    def validate_staff_ids(self, value):
        # Ensure all staff IDs are unique
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Staff IDs must be unique.")

        return value
