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
    modality_type = _ModalityTypeSummarySerializer()


class ModalitySerializer(ModalityListSerializer):
    """Serializer for retrieving a modality"""


# Request serializers
class ModalityCreateSerializer(serializers.Serializer):
    """Serializer for creating a modality"""

    name = serializers.CharField(required=True)
    modality_type_id = serializers.UUIDField(required=False)


class ModalityUpdateSerializer(serializers.Serializer):
    """Serializer for updating a modality"""

    name = serializers.CharField(required=False)
    modality_type_id = serializers.UUIDField(required=False)
