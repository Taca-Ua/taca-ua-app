from rest_framework import serializers


# Helper serializers
class SeasonModalityTypeSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)


# Response serializers
class SeasonListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)


# Request serializers
class SeasonCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
