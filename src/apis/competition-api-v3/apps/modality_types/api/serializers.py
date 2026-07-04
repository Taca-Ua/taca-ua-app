from apps.choices import TournamentCompetitorType
from rest_framework import serializers

from ..models import ModalityTypeModes


# Helper serializers
class ModalityTypeEscalaoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    min_participants = serializers.IntegerField(required=False, allow_null=True)
    max_participants = serializers.IntegerField(required=False, allow_null=True)
    points = serializers.ListField(child=serializers.IntegerField())


# Response serializers
class ModalityTypeListMinimalSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)


class ModalityTypeListSerializer(ModalityTypeListMinimalSerializer):
    description = serializers.CharField(allow_blank=True, allow_null=True)
    mode = serializers.CharField(max_length=20)
    tournament_competitor_type = serializers.CharField(max_length=20)


class ModalityTypeDetailSerializer(ModalityTypeListSerializer):
    escaloes = ModalityTypeEscalaoSerializer(many=True)


# Request serializers
class ModalityTypeCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(
        allow_blank=True, allow_null=True, required=False
    )
    escaloes = ModalityTypeEscalaoSerializer(many=True)
    mode = serializers.ChoiceField(choices=ModalityTypeModes.choices)
    tournament_competitor_type = serializers.ChoiceField(
        choices=TournamentCompetitorType.choices, required=False, allow_null=True
    )

    def validate(self, data):
        if data["mode"] == ModalityTypeModes.MODALITY and not data.get(
            "tournament_competitor_type"
        ):
            raise serializers.ValidationError(
                "tournament_competitor_type is required when mode is MODALITY."
            )
        return data

    season_id = serializers.IntegerField(required=False)


class ModalityTypeUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(
        allow_blank=True, allow_null=True, required=False
    )
    escaloes = ModalityTypeEscalaoSerializer(many=True, required=False)
