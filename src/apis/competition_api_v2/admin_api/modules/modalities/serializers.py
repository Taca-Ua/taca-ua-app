from rest_framework import serializers

from ..modality_types.serializers import ModalityTypeListSerializer


class ModalityListSerializer(serializers.Serializer):
    """Serializer for listing modalities"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    modality_type = ModalityTypeListSerializer()


class ModalitySerializer(ModalityListSerializer):
    """Serializer for retrieving a modality"""


class ModalityCreateSerializer(serializers.Serializer):
    """Serializer for creating a modality"""

    name = serializers.CharField(required=True)
    modality_type_id = serializers.UUIDField(required=False)


class ModalityUpdateSerializer(serializers.Serializer):
    """Serializer for updating a modality"""

    name = serializers.CharField(required=False)
    modality_type_id = serializers.UUIDField(required=False)
