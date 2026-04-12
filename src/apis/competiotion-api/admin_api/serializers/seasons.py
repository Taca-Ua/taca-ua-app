"""
Season management serializers
"""

from rest_framework import serializers


class SeasonListSerializer(serializers.Serializer):
    """Serializer for listing seasons"""

    id = serializers.UUIDField(read_only=True)
    year = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=["draft", "active", "finished"], read_only=True
    )
    created_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)
    started_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)
    finished_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)


class SeasonCreateSerializer(serializers.Serializer):
    """Serializer for creating a season"""

    year = serializers.IntegerField(required=True, min_value=2000)
