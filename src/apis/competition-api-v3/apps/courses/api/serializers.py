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
    nucleus = _NucleoSummarySerializer()
    logo_url = serializers.CharField(allow_null=True)

    belongs_to_season = serializers.BooleanField(required=False)


class CourseDetailSerializer(CourseListSerializer):
    """Serializer for course details"""

    relevant_season_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True
    )


# Request serializers
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
