from rest_framework import serializers

from ..models import Season


# Helper serializers
class SeasonModalityTypeSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)


# Response serializers
class SeasonListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    modality_types = serializers.SerializerMethodField()

    def get_modality_types(self, obj: Season):
        modality_types = obj.modality_types.all()
        return SeasonModalityTypeSummarySerializer(modality_types, many=True).data


# Request serializers
class SeasonCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
