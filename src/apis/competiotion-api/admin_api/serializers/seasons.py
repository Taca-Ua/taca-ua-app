"""
Season management serializers
"""

from rest_framework import serializers


class SeasonListSerializer(serializers.Serializer):
    """Serializer for listing seasons"""

    id = serializers.IntegerField(read_only=True)
    year = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=["draft", "active", "finished"], read_only=True
    )


class SeasonCreateSerializer(serializers.Serializer):
    """Serializer for creating a season"""

    year = serializers.IntegerField(required=True)
