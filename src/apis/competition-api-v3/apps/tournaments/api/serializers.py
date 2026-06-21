from rest_framework import serializers

from ..models import TournamentCompetitorType, TournamentFormat, TournamentStatus


# Helper serializers
class ModalitySummarySerializer(serializers.Serializer):
    """Serializer for modality summary"""

    id = serializers.UUIDField()
    name = serializers.CharField()


class ScoringFormatSummarySerializer(serializers.Serializer):
    """Serializer for scoring format summary"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    # rank = serializers.CharField()
    # points = serializers.ListField(child=serializers.IntegerField())


class TournamentSeasonSummarySerializer(serializers.Serializer):
    """Serializer for tournament season summary"""

    id = serializers.IntegerField()
    name = serializers.CharField()


class TournamentCompetitorSerializer(serializers.Serializer):
    """
    A competitor subscribed to a tournament.
    """

    id = serializers.UUIDField()
    entity_id = serializers.UUIDField()
    name = serializers.CharField()
    course_name = serializers.CharField()


class TournamentRankingPositionSerializer(serializers.Serializer):
    """Serializer for tournament ranking position"""

    competitor_id = serializers.UUIDField()
    position = serializers.IntegerField()


class TournamentRankSummarySerializer(serializers.Serializer):
    """Serializer for tournament rank summary"""

    name = serializers.CharField()
    points = serializers.ListField(child=serializers.IntegerField())


# Response serializers
class TournamentListSerializer(serializers.Serializer):
    """Serializer for listing tournaments"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.ChoiceField(choices=TournamentStatus.choices)
    modality = ModalitySummarySerializer()
    start_date = serializers.DateField(required=False, allow_null=True)
    mode = serializers.ChoiceField(choices=TournamentFormat.choices, required=False)


class TournamentDetailSerializer(TournamentListSerializer):
    """Serializer for tournament details"""

    competitor_type = serializers.ChoiceField(choices=TournamentCompetitorType.choices)
    competitors = TournamentCompetitorSerializer(many=True)
    scoring_format = ScoringFormatSummarySerializer()
    season = TournamentSeasonSummarySerializer()
    standings = TournamentRankingPositionSerializer(many=True, required=False)
    rank = TournamentRankSummarySerializer(required=False)
    format = serializers.CharField(required=False, source="tournament_format")
    format_data = serializers.DictField(required=False, allow_null=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Ensure competitors is an empty list if there are no competitors to avoid returning null
        representation["competitors"] = representation.get("competitors", []) or []

        return representation


# Request serializers
class TournamentCreateSerializer(serializers.Serializer):
    """Serializer for creating a tournament"""

    name = serializers.CharField(required=True)
    modality_id = serializers.UUIDField(required=True)
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    season_id = serializers.IntegerField(required=False)
    scoring_format_id = serializers.UUIDField(required=False)

    format = serializers.CharField(required=False, default="free")
    format_data = serializers.DictField(required=False, default={})


class TournamentUpdateSerializer(serializers.Serializer):
    """Serializer for updating a tournament"""

    name = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=TournamentStatus.choices, required=False)


class TournamentAddCompetitorsSerializer(serializers.Serializer):
    """Serializer for adding a competitors to a tournament"""

    entity_ids = serializers.ListField(child=serializers.UUIDField(), required=True)


class TournamentRemoveCompetitorsSerializer(serializers.Serializer):
    """Serializer for removing a competitors from a tournament"""

    competitor_ids = serializers.ListField(child=serializers.UUIDField(), required=True)


class TournamentFinishSerializer(serializers.Serializer):
    class _TournamentFinishEntrySerializer(serializers.Serializer):
        position = serializers.IntegerField(required=True)
        competitor_id = serializers.UUIDField(required=True)

    ranking_entries = _TournamentFinishEntrySerializer(many=True)


class TournamentFormatMetaUpdateSerializer(serializers.Serializer):
    """Serializer for updating tournament format meta"""

    format_meta = serializers.DictField(required=True)
