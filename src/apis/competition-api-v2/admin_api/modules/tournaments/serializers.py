"""
Tournament management serializers
"""

from rest_framework import serializers

STATUS_CHOICES = [
    ("draft", "Draft"),
    ("active", "Active"),
    ("finished", "Finished"),
]

COMPETITOR_TYPE_CHOICES = [
    ("team", "Team"),
    ("athlete", "Athlete"),
]


# Helpers serializers
class ModalitySummarySerializer(serializers.Serializer):
    """Serializer for modality summary"""

    id = serializers.UUIDField()
    name = serializers.CharField()


class ScoringFormatSummarySerializer(serializers.Serializer):
    """Serializer for scoring format summary"""

    name = serializers.CharField()
    rank = serializers.CharField()
    points = serializers.ListField(child=serializers.IntegerField())


# Response serializers
class TournamentCompetitorSerializer(serializers.Serializer):
    """
    A competitor subscribed to a tournament.
    """

    id = serializers.UUIDField()
    entity_id = serializers.UUIDField()
    name = serializers.CharField()
    course_name = serializers.CharField()


class TournamentListSerializer(serializers.Serializer):
    """Serializer for listing tournaments"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    modality = ModalitySummarySerializer()
    start_date = serializers.DateTimeField(required=False, allow_null=True)


class TournamentDetailSerializer(TournamentListSerializer):
    """Serializer for tournament details"""

    competitor_type = serializers.ChoiceField(choices=COMPETITOR_TYPE_CHOICES)
    competitors = TournamentCompetitorSerializer(many=True)
    scoring_format = ScoringFormatSummarySerializer()


# Request serializers
class TournamentListQuerySerializer(serializers.Serializer):
    """Serializer for tournament list query parameters"""

    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False)
    modality_id = serializers.UUIDField(required=False)


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

    class TournamentFinishEntrySerializer(serializers.Serializer):
        """Serializer for finishing a tournament entry"""

        position = serializers.IntegerField(required=True)
        competitor_id = serializers.UUIDField(required=True)

    ranking_entries = TournamentFinishEntrySerializer(many=True)


class TournamentCompetitorsAddEntrySerializer(serializers.Serializer):
    """Serializer for adding competitors to a tournament"""

    competitor_type = serializers.ChoiceField(
        choices=COMPETITOR_TYPE_CHOICES,
        required=True,
        help_text="Whether the competitor is a team or an athlete",
    )
    entity_id = serializers.UUIDField(
        required=True, help_text="ID of the team or athlete being added as a competitor"
    )


class TournamentCompetitorsDeleteSerializer(serializers.Serializer):
    """Serializer for deleting competitors from a tournament"""

    competitors_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )
