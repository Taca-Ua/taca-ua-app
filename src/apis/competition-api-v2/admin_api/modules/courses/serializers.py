"""
Course management serializers
"""

from rest_framework import serializers


# Helpers
class _NucleoSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()


# Response serializers
class CourseListSerializer(serializers.Serializer):
    """Serializer for listing courses"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    nucleo = _NucleoSummarySerializer()
    belongs_to_season = serializers.BooleanField()


class CourseDetailSerializer(CourseListSerializer):
    """Serializer for course details"""

    relevant_season_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True
    )


# Request serializers
class CourseListQuerySerializer(serializers.Serializer):
    """Serializer for course list query parameters"""

    season_id = serializers.IntegerField(required=False)


class CourseDetailQuerySerializer(serializers.Serializer):
    """Serializer for course get query parameters"""

    season_id = serializers.IntegerField(required=False)


class CourseCreateSerializer(serializers.Serializer):
    """Serializer for creating a course"""

    name = serializers.CharField(required=True)
    abbreviation = serializers.CharField(required=True)
    nucleo_id = serializers.UUIDField(required=True)


class CourseUpdateSerializer(serializers.Serializer):
    """Serializer for updating a course"""

    name = serializers.CharField(required=False)
    abbreviation = serializers.CharField(required=False)
    nucleo_id = serializers.UUIDField(required=False)


class CourseAddToSeasonSerializer(serializers.Serializer):
    """Serializer for adding a course to a season"""

    season_id = serializers.IntegerField(required=True)


class CourseRemoveFromSeasonSerializer(serializers.Serializer):
    """Serializer for removing a course from a season"""

    season_id = serializers.IntegerField(required=True)
