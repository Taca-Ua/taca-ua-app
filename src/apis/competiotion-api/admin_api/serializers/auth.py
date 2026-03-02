"""
Authentication serializers
"""

from rest_framework import serializers


class UserInfoSerializer(serializers.Serializer):
    user_id = serializers.CharField(read_only=True, help_text="Keycloak subject (UUID)")
    roles = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text="Realm-level roles from the Keycloak token",
    )
    username = serializers.CharField(
        read_only=True,
        allow_null=True,
        help_text="preferred_username from the token (if present)",
    )
