"""
Course management serializers
"""

from rest_framework import serializers


class CourseListSerializer(serializers.Serializer):
    """Serializer for listing courses"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    short_code = serializers.CharField()
    color = serializers.CharField(required=False, allow_blank=True)


class CourseCreateSerializer(serializers.Serializer):
    """Serializer for creating a course"""

    name = serializers.CharField(required=True)
    short_code = serializers.CharField(required=True)
    color = serializers.CharField(required=False, allow_blank=True)


class CourseUpdateSerializer(serializers.Serializer):
    """Serializer for updating a course"""

    name = serializers.CharField(required=False)
    short_code = serializers.CharField(required=False)
    color = serializers.CharField(required=False, allow_blank=True)
