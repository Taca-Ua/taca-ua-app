"""
Team management serializers
"""

from rest_framework import serializers


class TeamListSerializer(serializers.Serializer):
    """Serializer for listing teams"""

    id = serializers.UUIDField(read_only=True)
    modality_id = serializers.UUIDField()
    course_id = serializers.UUIDField()
    name = serializers.CharField()
    players = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_null=True
    )
    created_at = serializers.DateTimeField(read_only=True)


class TeamCreateSerializer(serializers.Serializer):
    """Serializer for creating a team"""

    modality_id = serializers.UUIDField(required=True)
    course_id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    players = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_null=True
    )


class TeamUpdateSerializer(serializers.Serializer):
    """Serializer for updating a team"""

    name = serializers.CharField(required=False, allow_blank=True)
    players_add = serializers.ListField(child=serializers.UUIDField(), required=False)
    players_remove = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
