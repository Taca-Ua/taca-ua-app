from rest_framework import serializers


# Helper serializers
class SeasonSummaryTournamentSummary(serializers.Serializer):
    finished = serializers.IntegerField()
    ongoing = serializers.IntegerField()
    scheduled = serializers.IntegerField()


class SeasonSummaryMatchesSummary(serializers.Serializer):
    finished = serializers.IntegerField()
    ongoing = serializers.IntegerField()
    scheduled = serializers.IntegerField()


class SeasonSummaryMembersSummary(serializers.Serializer):
    athletes = serializers.IntegerField()
    staff = serializers.IntegerField()


# Response serializers
class SeasonListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)


class SeasonSummarySerializer(SeasonListSerializer):
    """Serializer for season summary"""

    modality_types_count = serializers.IntegerField()
    active_modalities_count = serializers.IntegerField()
    active_courses_count = serializers.IntegerField()
    teams_count = serializers.IntegerField()
    tournaments_summary = SeasonSummaryTournamentSummary()
    matches_summary = SeasonSummaryMatchesSummary()
    members_summary = SeasonSummaryMembersSummary()


# Request serializers
class SeasonCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
