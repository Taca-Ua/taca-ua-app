"""
Student management serializers
"""

from rest_framework import serializers


class StudentListRequestSerializer(serializers.Serializer):
    """Serializer for listing students request parameters"""

    course_id = serializers.UUIDField(required=False)


class StudentListSerializer(serializers.Serializer):
    """Serializer for listing students"""

    id = serializers.UUIDField()
    full_name = serializers.CharField()

    course_name = serializers.CharField()
    student_number = serializers.CharField()
    is_member = serializers.BooleanField(default=False)


class StudentCreateSerializer(serializers.Serializer):
    """Serializer for creating a student"""

    full_name = serializers.CharField(required=True)
    course_id = serializers.UUIDField(required=True)
    student_number = serializers.CharField(required=True)
    is_member = serializers.BooleanField(required=False, default=False)


class StudentUpdateSerializer(serializers.Serializer):
    """Serializer for updating a student"""

    full_name = serializers.CharField(required=False)
    course_id = serializers.UUIDField(required=False)
    student_number = serializers.CharField(required=False)
    is_member = serializers.BooleanField(required=False)
