from rest_framework import serializers


class CourseSeasonParamSerializer(serializers.Serializer):
    """Serializer for course season context"""

    season_id = serializers.IntegerField(required=False)


class CourseListQueryParamsSerializer(serializers.Serializer):
    """Serializer for course list query params"""

    nucleo_id = serializers.UUIDField(required=False)
