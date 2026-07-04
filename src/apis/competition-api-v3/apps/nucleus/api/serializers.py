from rest_framework import serializers


# Helper serializers
class _NucleoCourseSummary(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()


# Response serializers
class NucleosListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    logo_url = serializers.URLField(required=False)


class NucleosDetailSerializer(NucleosListSerializer):
    courses = _NucleoCourseSummary(many=True)


# Request serializers
class NucleosCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=255)
    abbreviation = serializers.CharField(required=True, max_length=100)
    image = serializers.ImageField(required=False)


class NucleosUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, max_length=255)
    abbreviation = serializers.CharField(required=False, max_length=100)
    image = serializers.ImageField(required=False)
