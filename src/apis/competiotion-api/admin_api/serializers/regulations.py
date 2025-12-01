"""
Regulation management serializers
"""

from rest_framework import serializers


class RegulationListSerializer(serializers.Serializer):
    """Serializer for listing regulations"""

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    modality_id = serializers.IntegerField(required=False, allow_null=True)
    file_url = serializers.URLField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class RegulationCreateSerializer(serializers.Serializer):
    """Serializer for uploading a regulation"""

    file = serializers.FileField(required=True)
    title = serializers.CharField(required=True)
    modality_id = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)


class RegulationUpdateSerializer(serializers.Serializer):
    """Serializer for updating regulation metadata"""

    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    modality_id = serializers.IntegerField(required=False, allow_null=True)
