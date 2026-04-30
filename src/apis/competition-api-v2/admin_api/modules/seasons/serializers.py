"""
Season management serializers
"""

from rest_framework import serializers


class SeasonListSerializer(serializers.Serializer):
    """Serializer for listing seasons"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)


class SeasonCreateSerializer(serializers.Serializer):
    """Serializer for creating a season"""

    name = serializers.CharField(max_length=100)
