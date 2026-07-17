from rest_framework import serializers


# Helpers
class RankingCourseSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    logo_url = serializers.URLField(required=False, allow_null=True)


class RankingModalitySummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


# Response serializers
class RankingEntrySerializer(serializers.Serializer):
    course = RankingCourseSummarySerializer(source="*")
    points = serializers.IntegerField()
    extra_points = serializers.IntegerField()


class CourseModalityBreakdownRankingEntrySerializer(serializers.Serializer):
    modality = RankingModalitySummarySerializer(source="*")
    points = serializers.IntegerField()


class RankingAmmendmentSerializer(serializers.Serializer):
    season_id = serializers.IntegerField()
    course = RankingCourseSummarySerializer()
    modality = RankingModalitySummarySerializer(required=False)
    points = serializers.IntegerField()
    reason = serializers.CharField(required=False)


# Request serializers
class RankingAmmendmentCreateSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()
    modality_id = serializers.UUIDField(required=False, allow_null=True)
    points = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
