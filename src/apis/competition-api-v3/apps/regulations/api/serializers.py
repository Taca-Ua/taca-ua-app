from rest_framework import serializers


# Response serializers
class RegulationListSerializer(serializers.Serializer):
    """Serializer for listing regulations"""

    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    file_url = serializers.URLField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class RegulationDetailSerializer(RegulationListSerializer):
    """Serializer for retrieving a single regulation"""
    pass


# Request serializers
class RegulationCreateSerializer(serializers.Serializer):
    """Serializer for uploading a regulation"""

    file = serializers.FileField(required=True)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    season_id = serializers.IntegerField(required=False)


class RegulationUpdateSerializer(serializers.Serializer):
    """Serializer for updating regulation metadata"""

    file = serializers.FileField(required=False)
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
