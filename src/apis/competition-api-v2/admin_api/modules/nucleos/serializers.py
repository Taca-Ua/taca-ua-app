"""
Nucleos management serializers
"""

from rest_framework import serializers


class _NucleoCourseSummary(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()


# Response serializers
class NucleosListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()


class NucleosDetailSerializer(NucleosListSerializer):
    courses = _NucleoCourseSummary(many=True)


# Request serializers
class NucleosCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    abbreviation = serializers.CharField(required=True)


class NucleosUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    abbreviation = serializers.CharField(required=False)
