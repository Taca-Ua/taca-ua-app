"""
Course management serializers
"""

from rest_framework import serializers


class CourseListSerializer(serializers.Serializer):
    """Serializer for listing courses"""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    logo_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)


class CourseCreateSerializer(serializers.Serializer):
    """Serializer for creating a course"""

    name = serializers.CharField(required=True)
    abbreviation = serializers.CharField(required=True)
    description = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    logo_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)


class CourseUpdateSerializer(serializers.Serializer):
    """Serializer for updating a course"""

    name = serializers.CharField(required=False)
    abbreviation = serializers.CharField(required=False)
    description = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    logo_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
