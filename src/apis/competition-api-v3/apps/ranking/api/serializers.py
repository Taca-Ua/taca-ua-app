from rest_framework import serializers


# Helpers
class RankingCourseSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class RankingModalitySummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


# Response serializers
class GeneralRankingEntrySerializer(serializers.Serializer):
    course = RankingCourseSummarySerializer()
    points = serializers.IntegerField()


class ModalityRankingEntrySerializer(serializers.Serializer):
    course = RankingCourseSummarySerializer()
    points = serializers.IntegerField()


class CourseRankingBreakdownEntrySerializer(serializers.Serializer):
    modality = RankingModalitySummarySerializer()
    points = serializers.IntegerField()
