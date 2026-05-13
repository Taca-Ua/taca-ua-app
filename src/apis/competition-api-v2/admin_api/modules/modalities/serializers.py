from rest_framework import serializers


# Helper serializers
class _ModalityTypeSummarySerializer(serializers.Serializer):
    """Serializer for modality type summary"""

    id = serializers.UUIDField()
    name = serializers.CharField()


# Response serializers
class ModalityListSerializer(serializers.Serializer):
    """Serializer for listing modalities"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    belongs_to_season = serializers.BooleanField()
    modality_type = _ModalityTypeSummarySerializer(required=False)


class ModalitySerializer(ModalityListSerializer):
    """Serializer for retrieving a modality"""

    relevant_season_ids = serializers.ListField(
        child=serializers.IntegerField(), required=True, allow_empty=True
    )


# Request serializers
class ModalityListQuerySerializer(serializers.Serializer):
    """Serializer for modality list query parameters"""

    season_id = serializers.IntegerField(required=False)


class ModalityDetailQuerySerializer(serializers.Serializer):
    """Serializer for modality detail query parameters"""

    season_id = serializers.IntegerField(required=False)


class ModalityCreateSerializer(serializers.Serializer):
    """Serializer for creating a modality"""

    name = serializers.CharField(required=True)
    modality_type_id = serializers.UUIDField(required=False)


class ModalityUpdateSerializer(serializers.Serializer):
    """Serializer for updating a modality"""

    name = serializers.CharField(required=False)
    modality_type_id = serializers.UUIDField(required=False)
    season_id = serializers.IntegerField(required=False, allow_null=True)


class ModalityRemoveFromSeasonSerializer(serializers.Serializer):
    """Serializer for removing a modality from a season"""

    season_id = serializers.IntegerField(required=True)
