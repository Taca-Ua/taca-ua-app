from rest_framework import serializers


# Response serializers
class SeasonListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)


# Request serializers
class SeasonCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
