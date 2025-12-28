"""
Match management serializers
"""

from rest_framework import serializers


class NucleosListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()

    created_by = serializers.UUIDField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class NucleosCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    abbreviation = serializers.CharField(required=True)


class NucleosUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    abbreviation = serializers.CharField(required=False)
