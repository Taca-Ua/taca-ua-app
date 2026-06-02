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
    modality_type = ModalityModalityTypeSerializer(required=False)


class ModalityDetailSerializer(ModalityListSerializer):
    relevant_seasons_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )


# Request serializers
class ModalityCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    modality_type_id = serializers.UUIDField()


class ModalityUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    modality_type_id = serializers.UUIDField(required=False)


class ModalityAddToSeasonSerializer(serializers.Serializer):
    modality_type_id = serializers.UUIDField(required=True)
