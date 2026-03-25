"""
Nucleos management serializers
"""

from rest_framework import serializers


# Response serializers
class NucleosListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()


class NucleosDetailSerializer(NucleosListSerializer): ...


# Request serializers
class NucleosCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    abbreviation = serializers.CharField(required=True)


class NucleosUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    abbreviation = serializers.CharField(required=False)
