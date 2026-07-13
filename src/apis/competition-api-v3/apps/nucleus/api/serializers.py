from rest_framework import serializers

from ..models import Nucleus


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
    entity_type = serializers.ChoiceField(choices=Nucleus.NucleusEntityType.choices)
    logo_url = serializers.URLField(required=False)
    belongs_to_season = serializers.BooleanField(required=False)


class NucleosDetailSerializer(NucleosListSerializer):
    courses = _NucleoCourseSummary(many=True)

    relevant_season_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )


# Request serializers
class NucleosCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=255)
    abbreviation = serializers.CharField(required=True, max_length=100)
    image = serializers.ImageField(required=False)


class NucleosUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, max_length=255)
    abbreviation = serializers.CharField(required=False, max_length=100)
    image = serializers.ImageField(required=False)
    entity_type = serializers.ChoiceField(
        choices=Nucleus.NucleusEntityType.choices, required=False
    )
