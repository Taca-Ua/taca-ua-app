"""
Student management serializers
"""

from rest_framework import serializers


class StudentListSerializer(serializers.Serializer):
    """Serializer for listing students"""

    id = serializers.IntegerField(read_only=True)
    course_id = serializers.IntegerField()
    full_name = serializers.CharField()
    student_number = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    is_member = serializers.BooleanField(default=False)


class StudentCreateSerializer(serializers.Serializer):
    """Serializer for creating a student"""

    full_name = serializers.CharField(required=True)
    student_number = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    is_member = serializers.BooleanField(required=False, default=False)


class StudentUpdateSerializer(serializers.Serializer):
    """Serializer for updating a student"""

    full_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, allow_blank=True)
    is_member = serializers.BooleanField(required=False)
