"""
Team management serializers
"""

from rest_framework import serializers


class TeamListSerializer(serializers.Serializer):
    """Serializer for listing teams"""

    id = serializers.IntegerField(read_only=True)
    modality_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    name = serializers.CharField(required=False, allow_blank=True)
    players = serializers.ListField(child=serializers.IntegerField(), required=False)


class TeamCreateSerializer(serializers.Serializer):
    """Serializer for creating a team"""

    modality_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=False, allow_blank=True)
    players = serializers.ListField(child=serializers.IntegerField(), required=False)


class TeamUpdateSerializer(serializers.Serializer):
    """Serializer for updating a team"""

    name = serializers.CharField(required=False, allow_blank=True)
    players_add = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    players_remove = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
