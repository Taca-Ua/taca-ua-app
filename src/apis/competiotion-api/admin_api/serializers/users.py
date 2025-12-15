"""
User management serializers
"""

from rest_framework import serializers


class NucleoAdminListSerializer(serializers.Serializer):
    """Serializer for listing nucleo administrators"""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    email = serializers.EmailField()
    course_id = serializers.IntegerField()
    full_name = serializers.CharField(required=False, allow_blank=True)


class NucleoAdminCreateSerializer(serializers.Serializer):
    """Serializer for creating nucleo administrator"""

    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    course_id = serializers.IntegerField(required=True)
    course_abbreviation = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.CharField(required=False, allow_blank=True)


class NucleoAdminUpdateSerializer(serializers.Serializer):
    """Serializer for updating nucleo administrator"""

    course_id = serializers.IntegerField(required=False)
    course_abbreviation = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
