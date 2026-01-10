"""
Course management serializers
"""

from rest_framework import serializers


class CourseListSerializer(serializers.Serializer):
    """Serializer for listing courses"""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    nucleo = serializers.CharField()


class CourseDetailSerializer(CourseListSerializer):
    """Serializer for course details"""

    created_at = serializers.DateTimeField(read_only=True)


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
