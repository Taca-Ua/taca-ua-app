"""
Authentication serializers
"""

from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, help_text="Username")
    password = serializers.CharField(
        required=True, write_only=True, help_text="Password"
    )


class UserInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    course_id = serializers.IntegerField(read_only=True)
    course_abbreviation = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True, help_text="Session token")
    user = UserInfoSerializer(read_only=True, help_text="User information")
