from rest_framework import serializers


# Helper serializers
class ModalityModalityTypeSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)


# Response serializers
class ModalityListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)

    belongs_to_season = serializers.BooleanField(required=False)
    modality_type = ModalityModalityTypeSerializer(
        required=False, source="modality_type_data"
    )


class ModalityDetailSerializer(ModalityListSerializer):
    relevant_seasons_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    point_unit = serializers.CharField(max_length=255)


# Request serializers
class ModalityCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    modality_type_id = serializers.UUIDField()


class ModalityUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    modality_type_id = serializers.UUIDField(required=False)
    season_id = serializers.IntegerField(required=False, allow_null=True)
    point_unit = serializers.CharField(max_length=255, required=False, allow_null=True)

    def validate(self, attrs):
        modality_type_id = attrs.get("modality_type_id")
        season_id = attrs.get("season_id")

        if modality_type_id is not None and season_id is None:
            raise serializers.ValidationError(
                "Season ID must be provided when updating modality type."
            )

        return attrs


class ModalityAddToSeasonSerializer(serializers.Serializer):
    modality_type_id = serializers.UUIDField(required=True)
